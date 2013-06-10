package com.joshmoles.byobcontroller;

import java.util.Hashtable;

import android.app.ActionBar;
import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.res.Configuration;
import android.media.MediaPlayer;
import android.net.ConnectivityManager;
import android.os.Bundle;
import android.os.Vibrator;
import android.provider.Settings.Secure;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnTouchListener;
import android.widget.Button;
import android.widget.Toast;

import com.joshmoles.byobcontroller.ConfigurationWebXMLParser.ConfigEntry;
import com.joshmoles.byobcontroller.util.SystemUiHider;
import com.pubnub.api.Callback;
import com.pubnub.api.Pubnub;
import com.pubnub.api.PubnubException;

/**
 * An example full-screen activity that shows and hides the system UI (i.e.
 * status bar and navigation/system bar) with user interaction.
 *
 * @see SystemUiHider
 */


public class ControlActivity extends Activity {
	
    /**
     * The instance of pubnub shared between these functions.
     */
    Pubnub pubnub;
    boolean pubNubOn = false;
    
    ConfigEntry myConfig;
    
    String pass    		= null; // The password passed over from Main.
    String lobbyCh 		= null; // The channel used as the game lobby.
    String gameCh  		= null;	// The channel actually used for game broadcast communications.
    String privGameCh 	= null; // The channel for my control communications.
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_control);
        
        // Hide the action bar
        ActionBar actionBar = getActionBar();
        actionBar.hide();
        
		// Get the variables passed from super
		Bundle extras = getIntent().getExtras();
		if(extras != null) {
			pass = extras.getString(Consts.GAME_PASSWORD);
			Log.d(Consts.CONTROL_AREA, "Received extras from Loading.");
			myConfig = (ConfigEntry) getIntent().getParcelableExtra(Consts.CONFIG_OBJ);
		}
		
		// Go and configure all the touch listeners.
		registerOnTouchListeners();
		
		// Set up everything for pubnub.
		
		// Update the channel names.
		lobbyCh   	= Consts.LOBBY_PREFIX + pass;
		gameCh		= Consts.GAME_PREFIX + pass;
		privGameCh 	= Secure.getString(this.getContentResolver(), Secure.ANDROID_ID);
		
		// Go and configure pubnub
		configurePubnub();
    }
    
    /**
     * Function that does configuration of Pubnub for the controller.
     */
    private void configurePubnub() {
        // Configure PubNub object
        pubnub = new Pubnub(
        	    myConfig.pubnubPublish,  	// PUBLISH_KEY   (Optional, supply "" to disable)
        	    myConfig.pubnubSubscribe,   // SUBSCRIBE_KEY (Required)
        	    myConfig.pubnubSecret,      // SECRET_KEY    (Optional, supply "" to disable)
        	    "",      					// CIPHER_KEY    (Optional, supply "" to disable)
        	    false    					// SSL_ON?
        	);

        // In case of disconnect, register the receiver.
        this.registerReceiver(new BroadcastReceiver() {
            @Override
            public void onReceive(Context arg0, Intent intent) {
                pubnub.disconnectAndResubscribe();
            } 

        }, new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION));
        
        // Need to subscribe to the private user channel and the game channel.
        // First, the private user channel.
        Hashtable<String, String> args = new Hashtable<String, String>(2);
		args.put("channel", privGameCh);
		try {
			pubnub.subscribe(args, new Callback() {
			    public void successCallback(String channel, Object message) {
			    	// Callback for if a message is received in the game channel.
			    	// TODO: Update score, etc. here.
			    	Log.v(Consts.LOAD_FETCH, "Received Message " + message.toString());
			    	if(message.toString().equals(Consts.PUBNUB_RESP_GAMEOVER)) {
			    		// Game Over
			    		Log.v(Consts.LOAD_FETCH, "Attempting to play game over audio.");
			    		playAudio(R.raw.game_over);	
			    	} else if(message.toString().equals(Consts.PUBNUB_RESP_WINNER)){
			    		// Winner
			    		Log.v(Consts.LOAD_FETCH, "Attempting to play winner audio.");
			    		playAudio(R.raw.you_win);
			    	} else if(message.toString().equals(Consts.PUBNUB_RESP_LOSER)){
			    		// Loser
			    		Log.v(Consts.LOAD_FETCH, "Attempting to play loser audio.");
			    		playAudio(R.raw.you_lose);
			    	}

			    }

			    public void errorCallback(String channel, Object message) {
			        Log.w(Consts.LOAD_FETCH, channel + " " + message.toString());
			    }
			});
		} catch (PubnubException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
    
    /**
     * Plays raw game audio provided a resource location.
     * @param resource The android resource ID of audio to play.
     */
    private void playAudio(int resource) {
		MediaPlayer mediaPlayer = MediaPlayer.create(getApplicationContext(), resource);
		mediaPlayer.start();
		while(mediaPlayer.isPlaying())
			android.os.SystemClock.sleep(1000);
		mediaPlayer.release();
		Log.v(Consts.LOAD_FETCH,"Audio released");
    }
    
    /**
     * Configures all of the onTouch Listeners for each of the buttons.
     */
    private void registerOnTouchListeners() {
    	final Button upButton    = (Button) findViewById(R.id.buttonUp);
    	final Button downButton  = (Button) findViewById(R.id.buttonDown);
    	final Button leftButton  = (Button) findViewById(R.id.buttonLeft);
    	final Button rightButton = (Button) findViewById(R.id.buttonRight);
    	
    	upButton.setOnTouchListener(new OnTouchListener() {
            public boolean onTouch(View v, MotionEvent event) {
            	handleBtnPress("up", event.getAction());
                return true;
            }
        });
    	
    	downButton.setOnTouchListener(new OnTouchListener() {
            public boolean onTouch(View v, MotionEvent event) {
            	handleBtnPress("down", event.getAction());
                return true;
            }
        });
    	
    	leftButton.setOnTouchListener(new OnTouchListener() {
            public boolean onTouch(View v, MotionEvent event) {
            	handleBtnPress("left", event.getAction());
                return true;
            }
        });
    	
    	rightButton.setOnTouchListener(new OnTouchListener() {
            public boolean onTouch(View v, MotionEvent event) {
            	handleBtnPress("right", event.getAction());
                return true;
            }
        });
    	    	
    }
    
    private void btnVibrate() {
    	Vibrator vibe = (Vibrator) getApplicationContext().getSystemService(Context.VIBRATOR_SERVICE);
    	vibe.vibrate(Consts.VIBE_LENGTH);
    }
    
	private void handleBtnPress(String btn, int action) {
		
		// Only vibrate if the button was pressed down.
		if(action == MotionEvent.ACTION_DOWN) {
			btnVibrate();
		}
		
		// Only send a message if it is a down or up event on the buttons.
		if(action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_UP) {
	    	// Prepare to send a message over PubNub
	    	Hashtable<String, String> args = new Hashtable<String, String>(2);
	    	
	    	String dirS = "-"; 	// The direction the button was pressed
	    	
	    	// Put the channel on the args
	    	args.put("channel", privGameCh);
	   
	    	switch(action) {
	    	case MotionEvent.ACTION_DOWN: dirS = "-down"; break;
	    	case MotionEvent.ACTION_UP:   dirS = "-up"; break;
	    	}
	    		// Actually send the message to pubnub.
		    	args.put("message", btn + dirS);
		    	
		    	pubnub.publish(args, new Callback() {
		    	    public void successCallback(String channel, Object message) {
		    	        // Do nothing
		    	    }
		
		    	    public void errorCallback(String channel, Object message) {
			    		// Do nothing
		    	    }
		    	});
    	}
		
	}
    
    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);

        // Checks the orientation of the screen
        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            Toast.makeText(this, "landscape", Toast.LENGTH_SHORT).show();
        } else if (newConfig.orientation == Configuration.ORIENTATION_PORTRAIT){
            Toast.makeText(this, "portrait", Toast.LENGTH_SHORT).show();
        }
    }
    
    
}
