
 /******************************************************************************/
 
/******************************************************************************
 *         MSP430G2-LaunchPad CapTouch BoosterPack User Experience
 * 
 * This application operates on the LaunchPad platform using the MSP430G2452
 * device and the CapTouch BoosterPack plugin board. The capacitive touch and 
 * proximity sensing are enabled by the pin oscillator feature new to the 
 * MSP430G2xx2 family devices. The User Experience application also utilizes 
 * the cap touch library to realize & measure the capacitive touch and proximity
 * sensors. The cap touch library also provides layers of abstractions to 
 * generate higher logical outputs such as logical touches, geometry (in this 
 * hardware, a four-button wheel), and even gestures. 
 * 
 * The User Experience application starts up and remains in 'sleep' mode, 
 * sampling the proximity sensor every ~8.3ms [VLO/100=12kHz/100=120Hz]. Upon 
 * registering a valid proximity event [hand/finger/object hovering ~3-5cm from
 * the BoosterPack], the application wakes up to operate in the 'active' mode.
 * 
 * In active mode, the application samples and registers individual finger touches 
 * on the 16-position wheel or the center button as well as simple gestures 
 * [Clockwise & Counter-clockwise] while the finger moves along and remains on 
 * the wheel.      
 * 
 * a 9600 baud UART link is also implemented using SW TimerA to provide 
 * application and cap touch data back to the PC via the UART-USB back channel.
 * The application sends UART data upon events such as wake up, sleep, touch,
 * or gesture.
 ******************************************************************************/ 



#include "CTS_Layer.h"
#include "uart.h"


#define WAKE_UP_UART_CODE       0xBE
#define WAKE_UP_UART_CODE2      0xEF
#define SLEEP_MODE_UART_CODE    0xDE
#define SLEEP_MODE_UART_CODE2   0xAD
#define MIDDLE_BUTTON_CODE      0x80
#define WHEEL_POSITION_OFFSET   0x30

#define WHEEL_TOUCH_DELAY		    12			    //Delay between re-sendings of touches
#define MAX_IDLE_TIME           200
#define PROXIMITY_THRESHOLD     60

unsigned int wheel_position=ILLEGAL_SLIDER_WHEEL_POSITION, last_wheel_position=ILLEGAL_SLIDER_WHEEL_POSITION;
unsigned int deltaCnts[1];
unsigned int prox_raw_Cnts;




/*----------------- LED definition---------------------------------------------
 * There are 8 LEDs to represent different positions around the wheel. They are 
 * controlled by 5 pins of Port 1 using a muxing scheme. The LEDs are divided 
 * vertically into two groups of 4, in which each LED is paired up [muxed] with
 * the LED mirrored on the other side of the imaginary center vertical line via 
 * the use of pin P1.3 and one specific port pin. 
 * Specifically, the pairs are LEDs [0,7], [1,6], [2,5], [3,4], as shown in the 
 * diagram below.
 *     LED                        Position (degrees, clockwise)
 * --RIGHT SIDE--
 *      0       BIT4,!BIT3                  45
 *      1       BIT5,!BIT3                  80
 *      2       BIT6,!BIT3                 100
 *      3       BIT7,!BIT3                 135 *
 * 
 * --LEFT SIDE--
 *      4       BIT3,(BIT4,5,6)             225
 *      5       BIT3,(BIT4,5,7)             260
 *      6       BIT3,(BIT4,6,7)             280
 *      7       BIT3,(BIT5,6,7)             315
 *----------------------------------------------------------------------------*/
#define MASK7                   BIT4
#define MASK6                   BIT5
#define MASK5                   BIT6
#define MASK4                   BIT7

#define MASK3                   (BIT3+BIT4+BIT5+BIT6)
#define MASK2                   (BIT3+BIT4+BIT5+BIT7)
#define MASK1                   (BIT3+BIT4+BIT6+BIT7)
#define MASK0                   (BIT3+BIT5+BIT6+BIT7)

const unsigned char LedWheelPosition[16] = 
                                {
                                  MASK0, MASK0, MASK0 & MASK1, MASK1,
                                  MASK1 & MASK2, MASK2, MASK2 & MASK3, MASK3,
                                  MASK4, MASK4, MASK4 | MASK5, MASK5,
                                  MASK5 | MASK6,  MASK6, MASK6 | MASK7, MASK7
                                };
const unsigned char startSequence[8] = 
                                {
								    MASK0,
								    MASK1,
								    MASK2,
								    MASK3,
								    MASK4,
								    MASK5,
								    MASK6,
								    MASK7
								   };
/*----------------- LED definition------------------------------*/
 

void InitLaunchPadCore(void)

{
  BCSCTL1 |= DIVA_0;                    // ACLK/(0:1,1:2,2:4,3:8)
  BCSCTL3 |= LFXT1S_2;                  // LFXT1 = VLO  
  
  // Port init
  P1OUT &= ~(BIT3+BIT4+BIT5+BIT6+BIT7+BIT0);
  P1DIR |= BIT3+BIT4+BIT5+BIT6+BIT7+BIT0;
  P2SEL = 0x00;                         // No XTAL
  P2DIR |= (BIT0+BIT4+BIT2+BIT3+BIT1+BIT5);
  P2OUT &= ~(BIT0+BIT4+BIT2+BIT3+BIT1+BIT5);
}

void SendByte(unsigned char touch)
{
  TimerA_UART_init();
  TimerA_UART_tx(touch);
  TimerA_UART_shutdown();  
}
 
/* ----------------CapTouchIdleMode-----------------------------------------
 * Device stays in LPM3 'sleep' mode, only Proximity Sensor is used to detect 
 * any movement triggering device wake up                                  
 * ------------------------------------------------------------------------*/ 
void CapTouchIdleMode(void)
{ 
  /* Send status via UART: 'sleep' = [0xDE, 0xAD] */  
  SendByte(SLEEP_MODE_UART_CODE);
  SendByte(SLEEP_MODE_UART_CODE2);
  
  /* Set DCO to 1MHz */
  /* Set SMCLK to 1MHz / 8 = 125kHz */
  BCSCTL1 = CALBC1_1MHZ;                
  DCOCTL = CALDCO_1MHZ;
  BCSCTL2 |= DIVS_3;  
  
  P1OUT |= BIT0;                            // Turn on center LED    
  deltaCnts[0] = 0;
  
  /* Sleeping in LPM3 with ACLK/100 = 12Khz/100 = 120Hz wake up interval */
  /* Measure proximity sensor count upon wake up */
  /* Wake up if proximity deltaCnts > THRESHOLD */  
  do
  {
    TACCR0 = 100;				                       							                                
    TACTL = TASSEL_1 + MC_1;                   
    TACCTL0 |= CCIE;    
    __bis_SR_register(LPM3_bits+GIE);
    TACCTL0 &= ~CCIE;                             
    TI_CAPT_Custom(&proximity_sensor,deltaCnts);
  }
  while (deltaCnts[0] <= PROXIMITY_THRESHOLD);
  
  P1OUT &= ~BIT0;                           // Turn off center LED
}
 
/* ----------------MeasureCapBaseLine--------------------------------------
 * Re-measure the baseline capacitance of the wheel elements & the center  
 * button. To be called after each wake up event.                          
 * ------------------------------------------------------------------------*/
void MeasureCapBaseLine(void)
{
  P1OUT = BIT0;
  /* Set DCO to 8MHz */
  /* SMCLK = 8MHz/8 = 1MHz */
  BCSCTL1 = CALBC1_8MHZ;     
  DCOCTL = CALDCO_8MHZ;
  BCSCTL2 |= DIVS_3;
  
  TI_CAPT_Init_Baseline(&wheel);
  TI_CAPT_Update_Baseline(&wheel,2);
  TI_CAPT_Init_Baseline(&middle_button);
  TI_CAPT_Update_Baseline(&middle_button,2);  
}

/* ----------------LedStartUpSequence--------------------------------------
 * Display an LED lighting sequence to indicate the wake up event
 * ------------------------------------------------------------------------*/
void LedStartUpSequence(void)
{
  unsigned char i;
  TACCTL0 = CCIE;                           // CCR0 interrupt enabled
  TACTL |= TACLR;
  TACCR0 = TAR + 500;                       // 50ms                             
  TACTL = TASSEL_1 + MC_1;                  // ACLK, upmode
  
  /* Slow clockwise sequence */
  for(i=0; i<8; i++)
  {
      P1OUT = startSequence[i];
      __bis_SR_register(LPM3_bits+GIE);
     
      __delay_cycles(1000000);
      TACCR0 = TAR + 500;   // 50ms                             
  }

  P1OUT = BIT0;
  /* Fast counter-clockwise sequence */
  while(i)
  {
      i--;
      P1OUT = startSequence[i];
      __bis_SR_register(LPM3_bits+GIE);
      TACCR0 = TAR + 500;   // 50ms                             
  }
  TACCTL0 &= ~CCIE;                         // CCR0 interrupt disabled
  P1OUT = 0;                                // Turn off all LEDs
}


/* ----------------CapTouchActiveMode----------------------------------------------
 * Determine immediate gesture based on current & previous wheel position
 * 
 * 
 * 
 * 
 * 
 * 
 * 
 * -------------------------------------------------------------------------------*/
void CapTouchActiveMode()
{
  unsigned char idleCounter, activeCounter;
  unsigned char centerButtonTouched = 0;
  unsigned int wheelTouchCounter = WHEEL_TOUCH_DELAY - 1;
  
  /* Send status via UART: 'wake up' = [0xBE, 0xEF] */  
  SendByte(WAKE_UP_UART_CODE);
  SendByte(WAKE_UP_UART_CODE2);

  idleCounter = 0;      
  activeCounter = 0;
  
  while (idleCounter++ < MAX_IDLE_TIME)
  {  
	  /* Set DCO to 8MHz */
	  /* SMCLK = 8MHz/8 = 1MHz */
    BCSCTL1 = CALBC1_8MHZ;     
    DCOCTL = CALDCO_8MHZ;
    BCSCTL2 |= DIVS_3;  
    TACCTL0 &= ~CCIE;   
    
    wheel_position = ILLEGAL_SLIDER_WHEEL_POSITION;       
    wheel_position = TI_CAPT_Wheel(&wheel);
    
    /* Process wheel touch/position/gesture  if a wheel touch is registered*/
    /* Wheel processing has higher priority than center button*/
    
    if(wheel_position != ILLEGAL_SLIDER_WHEEL_POSITION)
    {
      centerButtonTouched = 0;
      
      /* Adjust wheel position based: rotate CCW by 2 positions */
      if (wheel_position < 0x08)
      {
         wheel_position += 0x40 - 0x08;
      }
      else
      {
         wheel_position -= 0x08;
            /* Adjust wheel position based: rotate CCW by 2 positions */
      }
      
      wheel_position = wheel_position >>2;  // divide by four
               
      
      /* Add hysteresis to reduce toggling between wheel positions if no gesture 
       * has been TRULY detected. */  

      if (last_wheel_position != ILLEGAL_SLIDER_WHEEL_POSITION)
            wheel_position = last_wheel_position;

      
      /* Turn on corresponding LED(s) */
      P1OUT = (P1OUT & BIT0) | LedWheelPosition[wheel_position];
      
     
      if (++wheelTouchCounter >= WHEEL_TOUCH_DELAY)
          {
          	/* Transmit wheel position [twice] via UART to PC */
          	wheelTouchCounter = 0;
          	SendByte(wheel_position + WHEEL_POSITION_OFFSET );
          	SendByte(wheel_position + WHEEL_POSITION_OFFSET );
          }
        
       else
       	 {  wheelTouchCounter = WHEEL_TOUCH_DELAY - 1;

       			idleCounter = 0;                      // Reset idle counter
       			activeCounter++;
       			last_wheel_position = wheel_position;
       	 }
     }
 else{
      if(TI_CAPT_Button(&middle_button))
      { /* Middle button was touched */   
        if (centerButtonTouched==0)
        {
          /* Transmit center button code [twice] via UART to PC */
          SendByte(MIDDLE_BUTTON_CODE);          
          SendByte(MIDDLE_BUTTON_CODE);
                    
          centerButtonTouched = 1;

          P1OUT = (P1OUT&BIT0) ^ BIT0;      // Toggle Center LED
        }
        idleCounter = 0;
      }
      else    
      { /* No touch was registered at all [Not wheel or center button */
        centerButtonTouched = 0;
        P1OUT &= BIT0;

          if (last_wheel_position  != ILLEGAL_SLIDER_WHEEL_POSITION)
            {
              /* Transmit last wheel position [twice] via UART to PC */
              SendByte(last_wheel_position  + WHEEL_POSITION_OFFSET );
              SendByte(last_wheel_position  + WHEEL_POSITION_OFFSET );
              wheelTouchCounter = WHEEL_TOUCH_DELAY - 1;
            }

      }
      
      // Reset all touch conditions, turn off LEDs, 
      last_wheel_position= ILLEGAL_SLIDER_WHEEL_POSITION;      

    } 
    
  /* ------------------------------------------------------------------------
   * Option:
   * Add delay/sleep cycle here to reduce active duty cycle. This lowers power
   * consumption but sacrifices wheel responsiveness. Additional timing 
   * refinement must be taken into consideration when interfacing with PC
   * applications GUI to retain proper communication protocol.
   * -----------------------------------------------------------------------*/
     
  } 
}


void main(void)
{   

  WDTCTL = WDTPW + WDTHOLD;             // Stop watchdog timer
  
  InitLaunchPadCore();
    
  
  /* Set DCO to 1MHz */
  /* Set SMCLK to 1MHz / 8 = 125kHz */
  BCSCTL1 = CALBC1_1MHZ;                
  DCOCTL = CALDCO_1MHZ;
  BCSCTL2 |= DIVS_3;
  /* Establish baseline for the proximity sensor */  
  TI_CAPT_Init_Baseline(&proximity_sensor);
  TI_CAPT_Update_Baseline(&proximity_sensor,5);
  
  while (1)
  {
    CapTouchIdleMode();  
  
    MeasureCapBaseLine();
    LedStartUpSequence();
    CapTouchActiveMode();
  }
}
