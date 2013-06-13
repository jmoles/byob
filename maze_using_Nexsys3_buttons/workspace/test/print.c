/********************************************
 * Created By: Tejashree Chaudhari
 * 			   Dimitriy Labnsky
 * 			   Josh Moles
 * 			   Tejas Tapsale
 *****************************************/
/******************************************
 *This code detects which pushbutton is pressed or released using key-debounce technique.
 *According to the pushbutton pressed or released for each operation individual code/data is
 *sent out using UART*/

/********** Include Files ***********/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "mb_interface.h"
#include "xparameters.h"
#include "xbasic_types.h"
#include "xgpio.h"

// Microblaze Cache Parameters
#define	USE_ICACHE				XPAR_MICROBLAZE_0_USE_ICACHE
#define	USE_DCACHE				XPAR_MICROBLAZE_0_USE_DCACHE
#define USE_DCACHE_WRITEBACK	XPAR_MICROBLAZE_DCACHE_USE_WRITEBACK

// Declarations
#define BTN_GPIO_DEVICEID		XPAR_PUSH_BUTTONS_4BITS_DEVICE_ID
#define LED_GPIO_DEVICEID		XPAR_LEDS_8BITS_DEVICE_ID

#define MASK_BUTTONS			0x0010
#define DEFAULT_CHANNEL         1

// Peripheral instances
XGpio BTNInst, LEDInst;

// Function declarations
XStatus init_peripherals(void);
void	delay(int count);

int main()
{

    XStatus sts;

	// Enable the Microblaze caches and
	// kick off the processing by enabling the Microblaze interrupt

	if (USE_ICACHE == 1)
	{
		microblaze_invalidate_icache();
		microblaze_enable_icache();
	}
	if (USE_DCACHE == 1)
	{
		microblaze_invalidate_dcache();
		microblaze_enable_dcache();
	}
	 microblaze_enable_interrupts();


    // initialize the peripherals
    sts = init_peripherals();
    if (sts != XST_SUCCESS)
    {
    	xil_printf("FATAL ERROR: Could not initialize the peripherals\n\r");
		xil_printf("Please power cycle or reset the system\n\r");
		return -1;
    }


	while(1)
	{
		u32 btnsw, old_btnsw, button;

		btnsw = XGpio_DiscreteRead(&BTNInst, DEFAULT_CHANNEL);	//read the pushbutton switches
		delay(10000);
		old_btnsw = btnsw;

		if(btnsw == 0x0001)	//for UP button
		{
			xil_printf("0%x\r\n", btnsw); //send out key pressed
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, btnsw);	//display respective LEDs

			do
			{	//check for key debouce: if key is still pressed
				delay(10000);
				btnsw = XGpio_DiscreteRead(&BTNInst, DEFAULT_CHANNEL);	//read the pushbutton switches
			}while(btnsw == old_btnsw);
			button = old_btnsw | MASK_BUTTONS;
			xil_printf("%x\r\n", button);	//send out key released
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, button);	//display respective LEDs
		}
		else if(btnsw == 0x0002)	//for LEFT button
		{
			xil_printf("0%x\r\n", btnsw);	//send out key pressed
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, btnsw);	//display respective LEDs

			do
			{
				delay(10000);
				btnsw = XGpio_DiscreteRead(&BTNInst, DEFAULT_CHANNEL);	//read the pushbutton switches
			}while(btnsw == old_btnsw);
			button = old_btnsw | MASK_BUTTONS;
			xil_printf("%x\r\n", button);	//send out key released
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, button);	//display respective LEDs
		}
		else if(btnsw == 0x0004)	//DOWN button
		{
			xil_printf("0%x\r\n", btnsw);	//send out key pressed
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, btnsw);	//display respective LEDs

			do
			{
				delay(10000);
				btnsw = XGpio_DiscreteRead(&BTNInst, DEFAULT_CHANNEL);	//read the pushbutton switches
			}while(btnsw == old_btnsw);
			button = old_btnsw | MASK_BUTTONS;
			xil_printf("%x\r\n", button);	//send out key released
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, button);	//display respective LEDs
		}
		else if(btnsw == 0x0008)	//RIGHT button
		{
			xil_printf("0%x\r\n", btnsw);	//send out button pressed
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, btnsw);	//display respective LEDs

			do
			{
				delay(10000);
				btnsw = XGpio_DiscreteRead(&BTNInst, DEFAULT_CHANNEL);	//read the pushbutton switches
			}while(btnsw == old_btnsw);	//send out button released
			button = old_btnsw | MASK_BUTTONS;
			xil_printf("%x\r\n", button);
			XGpio_DiscreteWrite(&LEDInst, DEFAULT_CHANNEL, button);	//display respective LEDs
		}

	}


}

//delay() -generate delay
void delay(int count)
{
	int i;
	for(i=0; i<count; i++)
	{}
}



// init_peripherals() - Initializes the peripherals
XStatus init_peripherals(void)
{

	//***** INSERT YOUR PERIPHERAL INITIALIZATION CODE HERE ******//
	XStatus Status;
	//GPIO Initialize
	Status = XGpio_Initialize(&BTNInst, BTN_GPIO_DEVICEID);
		if (Status != XST_SUCCESS)
		{
			xil_printf("Init ERROR: GPIO Initialization Failed \r\n");
			return XST_FAILURE;
		}
	XGpio_SetDataDirection(&BTNInst, DEFAULT_CHANNEL, 0xFF);	//Input data direction for last 4 bits

	//LEDs Initialize
	Status = XGpio_Initialize(&LEDInst, LED_GPIO_DEVICEID);
		if (Status != XST_SUCCESS)
		{
			xil_printf("Init ERROR: LED Initialization Failed \r\n");
			return XST_FAILURE;
		}
	XGpio_SetDataDirection(&LEDInst, DEFAULT_CHANNEL, 0x00);	//set output direction


	return XST_SUCCESS;
}