package com.joshmoles.byobcontroller;

import java.util.concurrent.CancellationException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import com.joshmoles.byobcontroller.ConfigurationWebXMLParser.ConfigEntry;


import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.view.MenuItem;
import android.widget.Toast;
import android.support.v4.app.NavUtils;

public class Loading extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		String pass = null;  // The password passed over from Main.
		
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

		String url = Consts.BASE_URL + "/getconfig/" + pass;
		Log.i(Consts.LOAD_FETCH, "URL is " + url);
		
		ConnectivityManager connMgr = (ConnectivityManager)
			getSystemService(Context.CONNECTIVITY_SERVICE);
		NetworkInfo networkInfo = connMgr.getActiveNetworkInfo();
		if(networkInfo != null && networkInfo.isConnected()) {
			// Execute the download of the page data.
			AsyncTask<String, Void, ConfigEntry> myTask = new DownloadWebPageTask(this).execute(url);
			// Wait for the task to finish.
			try {
				// Attempt to grab result from thread with a timeout.
				ConfigEntry result = 
						myTask.get(Consts.XML_FETCH_TIMEOUT, TimeUnit.MILLISECONDS);
				
				// Check if it was cancelled, if so, navigate up.
				if(myTask.isCancelled()) {
					NavUtils.navigateUpFromSameTask(this);
				}
	    		
				// Ensure result is not null and then start new intent.
				if(result != null) {
					Intent intent = new Intent(this, ControlActivity.class);
					intent.putExtra(Consts.PUBNUB_OBJ, result);
					this.startActivity(intent);
				}
			} catch (InterruptedException e) {
				e.printStackTrace();
				networkFetchFailed();
			} catch (ExecutionException e) {
				e.printStackTrace();
				networkFetchFailed();
			} catch (TimeoutException e) {
				e.printStackTrace();
				networkFetchFailed();
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
	
	private void networkFetchFailed() {
		Toast.makeText(Loading.this, 
				getString(R.string.network_exception), 
				Toast.LENGTH_SHORT).show();
		NavUtils.navigateUpFromSameTask(this);
		
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
			NavUtils.navigateUpFromSameTask(this);
			return true;
		}
		return super.onOptionsItemSelected(item);
	}

}
