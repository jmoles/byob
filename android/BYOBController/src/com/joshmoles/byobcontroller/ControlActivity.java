package com.joshmoles.byobcontroller;

import java.util.Hashtable;

import com.joshmoles.byobcontroller.util.SystemUiHider;

import android.app.ActionBar;
import android.app.Activity;
import android.content.res.Configuration;
import android.os.Bundle;
import android.view.View;
import android.widget.RelativeLayout;
import android.widget.Toast;

import com.pubnub.api.Callback;
import com.pubnub.api.Pubnub;

/**
 * An example full-screen activity that shows and hides the system UI (i.e.
 * status bar and navigation/system bar) with user interaction.
 *
 * @see SystemUiHider
 */
public class ControlActivity extends Activity {
	
	
    /**
     * The instance of pubnub shared between these functions.
     * Also, a few constants used between them.
     */
    Pubnub pubnub;
    private final String PUBNUB_CHANNEL = "player_control";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_control);
        
        // Hide the action bar
        ActionBar actionBar = getActionBar();
        actionBar.hide();
        
        // Build the Pubnub stuff
        pubnub = new Pubnub(
        	    getString(R.string.publish_key),     // PUBLISH_KEY   (Optional, supply "" to disable)
        	    getString(R.string.subscribe_key),   // SUBSCRIBE_KEY (Required)
        	    getString(R.string.secret_key),      // SECRET_KEY    (Optional, supply "" to disable)
        	    "",      							 // CIPHER_KEY    (Optional, supply "" to disable)
        	    false    							 // SSL_ON?
        	);
        
    }
    
    /**
     * Listener for all of the buttons
     * 
     */
    public void onClick(View v) {
    	// Preapare to send a message over PubNub
    	Hashtable<String, String> args = new Hashtable<String, String>(2);
    	
    	String message = "null";
    	
    	// Put the channel on the args
    	args.put("channel", PUBNUB_CHANNEL);
    	
    	
    	switch(v.getId()) {
    	case R.id.buttonUp:
    		message = "up";
    		break;
    	case R.id.buttonDown:
    		message = "down";
    		break;
    	case R.id.buttonLeft:
    		message = "left";
    		break;
    	case R.id.buttonRight:
    		message = "right";
    		break;
    	case R.id.buttonA:
    		message = "A";
    		break;
    	case R.id.buttonB:
    		message = "B";
    		break;
    	}
    	
    	args.put("message", message);
    	
    	pubnub.publish(args, new Callback() {
    	    public void successCallback(String channel, Object message) {
    	        // Do nothing
    	    }

    	    public void errorCallback(String channel, Object message) {
    	    	notifyUser("FAILED TO SEND" + channel + " : " + message.toString());
    	    }
    	});
    }
    
    private void notifyUser(final String toastStr) {
    	runOnUiThread(new Runnable() {
    		public void run() {
    			Toast.makeText(ControlActivity.this, toastStr, Toast.LENGTH_SHORT).show();
    		}
    	});
    }
    
    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);

        // Checks the orientation of the screen
        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
        	final RelativeLayout btnLayout = 
        			(RelativeLayout) findViewById(R.id.buttonLayout);
        	RelativeLayout.LayoutParams params = 
        			(RelativeLayout.LayoutParams) btnLayout.getLayoutParams();
        	//TODO: Need to finish updating the parameters here.
        	
            Toast.makeText(this, "landscape", Toast.LENGTH_SHORT).show();
        } else if (newConfig.orientation == Configuration.ORIENTATION_PORTRAIT){
            Toast.makeText(this, "portrait", Toast.LENGTH_SHORT).show();
        }
    }
    
    
}
