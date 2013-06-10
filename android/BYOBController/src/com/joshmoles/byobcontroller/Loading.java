package com.joshmoles.byobcontroller;

import java.util.Hashtable;
import java.util.concurrent.CancellationException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import com.joshmoles.byobcontroller.ConfigurationWebXMLParser.ConfigEntry;
import com.pubnub.api.Callback;
import com.pubnub.api.Pubnub;
import com.pubnub.api.PubnubException;


import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.provider.Settings.Secure;
import android.util.Log;
import android.view.MenuItem;
import android.widget.Toast;
import android.support.v4.app.NavUtils;

public class Loading extends Activity {
	
	Pubnub pubnub;			// The pubnub object for communications.
	ConfigEntry result;  	// The config entry if retrieved successfully.
	String pass = null;  	// The password passed over from Main.
	
	// Handler for callbacks to UI thread.
	final Handler mHandler = new Handler();
	
	// String for passing back to UI thread to move back up to main.
	protected String mResults = null;
	
	// Used to print error and go back to main.
	final Runnable mGoBackToMain = new Runnable() {
		public void run() {
			goBackFailure(mResults);
		}
	};
	
	// Used to change activity to the control activity.
	final Runnable mGoToControl = new Runnable() {
		public void run() {
			startControlActivity();
		}
	};

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_loading);
		// Show the Up button in the action bar.
		setupActionBar();
		
		// Get the variables passed from super
		Bundle extras = getIntent().getExtras();
		if(extras != null) {
			pass = extras.getString(Consts.GAME_PASSWORD);
		}
		
		if(pass == null) {
			// Pop up an error and go back.
			Toast.makeText(Loading.this, 
					getString(R.string.toast_no_string_error), 
					Toast.LENGTH_SHORT).show();			
			NavUtils.navigateUpFromSameTask(this);
			
		}
		
		// Attempt to fetch the PubNub configuration information with provided password.

		String url = Consts.BASE_URL + "/client/getconfig/" + pass;
		Log.d(Consts.LOAD_FETCH, "URL is " + url);
		
		ConnectivityManager connMgr = (ConnectivityManager)
			getSystemService(Context.CONNECTIVITY_SERVICE);
		NetworkInfo networkInfo = connMgr.getActiveNetworkInfo();
		if(networkInfo != null && networkInfo.isConnected()) {
			// Execute the download of the page data.
			AsyncTask<String, Void, ConfigEntry> myTask = new DownloadWebPageTask(this).execute(url);
			// Wait for the task to finish.
			try {
				// Attempt to grab result from thread with a timeout.
				result = 
						myTask.get(Consts.XML_FETCH_TIMEOUT, TimeUnit.MILLISECONDS);
				
				// Check if it was cancelled, if so, navigate up.
				if(myTask.isCancelled()) {
					NavUtils.navigateUpFromSameTask(this);
				}
	    		
				// Ensure result is not null and attempt to join a game.
				if(result != null) {
					attemptToJoin(result, pass);
				}
			} catch (InterruptedException e) {
				e.printStackTrace();
				goBackFailure();
			} catch (ExecutionException e) {
				e.printStackTrace();
				goBackFailure();
			} catch (TimeoutException e) {
				e.printStackTrace();
				goBackFailure();
			} catch (CancellationException e) {
				// Thread was cancelled (likely from 404 error).
				Toast.makeText(this, getString(R.string.invalid_password),
						Toast.LENGTH_SHORT).show();
				NavUtils.navigateUpFromSameTask(this);
			}
			// Task fetch completed.
			
		} else {
			// No network connection is available.
			Toast.makeText(Loading.this, 
					getString(R.string.toast_no_connection_error), 
					Toast.LENGTH_SHORT).show();
			NavUtils.navigateUpFromSameTask(this);
			
		}
		

		
	}
	
	/**
	 * Function called when attempting to join a game.
	 */
	private void attemptToJoin(ConfigEntry result, String pass) {		
		// Create a new pubnub object.
		pubnub = new Pubnub(
        	    result.pubnubPublish,  // PUBLISH_KEY   (Optional, supply "" to disable)
        	    result.pubnubSubscribe,  // SUBSCRIBE_KEY (Required)
        	    result.pubnubSecret,      // SECRET_KEY    (Optional, supply "" to disable)
        	    "",      // CIPHER_KEY    (Optional, supply "" to disable)
        	    false    // SSL_ON?
        	);
		
		Log.d(Consts.LOAD_FETCH, result.toString());
		
		// Subscribe in an attempt to find server to join.
		Hashtable<String, String> args = new Hashtable<String, String>(2);
		String myIDCh = Secure.getString(this.getContentResolver(), Secure.ANDROID_ID);
		Log.d(Consts.LOAD_FETCH, "ANDROID ID Channel is " + myIDCh + ".");
		String lobbCh = Consts.LOBBY_PREFIX + pass;
		
		// Subscribe to my ANDROID_ID channel.
		args.put("channel", myIDCh);
		try {
			pubnub.subscribe(args, new Callback() {
			    public void successCallback(String channel, Object message) {
			    	// This is the callback if we receive a message on our ID channel.
			    	
			    	Log.d(Consts.LOAD_FETCH, "Received Message " + message.toString());

			    	if(message.toString().equals(Consts.PUBNUB_RESP_GAMEFULL)) {
			    		// Game is full if this is response. Clean up and go back.
			    		Log.d(Consts.LOAD_FETCH, "Game is presently full.");
			    		mResults = getString(R.string.game_full);
			    		mHandler.post(mGoBackToMain);
			    	} else if(message.toString().equals(Consts.PUBNUB_RESP_GAMERDY)) {
				    	// This means we are basically getting invited to join the game.
				    	// Go ahead and unsubscribe from all Pubnub and start control activity.
			    		pubnub.unsubscribeAll();
			    		mHandler.post(mGoToControl);
			    	}
			    }

			    public void errorCallback(String channel, Object message) {
			        Log.w(Consts.LOAD_FETCH, channel + " " + message.toString());
		    		mResults = getString(R.string.network_exception);
		    		mHandler.post(mGoBackToMain);
			    }
			});
		} catch (PubnubException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		// Now, make a message to send and publish it to the lobby channel.
		args.put("channel", lobbCh);
		args.put("message", "want-to-join-byob: " + myIDCh);
		
		pubnub.publish(args, new Callback() {
		    public void successCallback(String channel, Object message) {
		        // Do nothing
		    }
			
		    public void errorCallback(String channel, Object message) {
		    	Log.w(Consts.LOAD_FETCH, message.toString());
		    	goBackFailure();
		    }
		});
		
		
	}
	
	/**
	 * Function to change over to the control activity.
	 */
	
	private void startControlActivity() {
		Intent intent = new Intent(this, ControlActivity.class);
		intent.putExtra(Consts.CONFIG_OBJ, result);
		intent.putExtra(Consts.GAME_PASSWORD, pass);
		this.startActivity(intent);
	}
	
	
	/**
	 * Function that prints an error for user when network connection
	 * fails.
	 */
	private void goBackFailure(String errorString) {
		pubnub.unsubscribeAll();
		Toast.makeText(Loading.this, 
				errorString, 
				Toast.LENGTH_SHORT).show();
		NavUtils.navigateUpFromSameTask(this);
		
	}
	
	private void goBackFailure() {
		goBackFailure(getString(R.string.network_exception));
	}

	/**
	 * Set up the {@link android.app.ActionBar}.
	 */
	private void setupActionBar() {
		getActionBar().setDisplayHomeAsUpEnabled(true);

	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		switch (item.getItemId()) {
		case android.R.id.home:
			// This ID represents the Home or Up button. In the case of this
			// activity, the Up button is shown. Use NavUtils to allow users
			// to navigate up one level in the application structure. For
			// more details, see the Navigation pattern on Android Design:
			//
			// http://developer.android.com/design/patterns/navigation.html#up-vs-back
			//
			pubnub.unsubscribeAll();
			NavUtils.navigateUpFromSameTask(this);
			return true;
		}
		pubnub.unsubscribeAll();
		return super.onOptionsItemSelected(item);
	}

}
