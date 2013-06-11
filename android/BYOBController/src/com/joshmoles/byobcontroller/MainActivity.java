/**
 * Project: ECE 544 Final Project
 * Primary Author: Josh Moles
 * Teammates: Dimitriy A. Labunsky, Tejashree Chaudhari, Tejas Tapsale
 *
 * Demonstration Date: June 11, 2013
 * 
 * Description: Start screen of game.
 * 
 * The MIT License (MIT)
 * 
 * Copyright (c) 2013 Josh Moles
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package com.joshmoles.byobcontroller;

import android.os.Bundle;
import android.app.Activity;
import android.content.Intent;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;
import android.support.v4.app.NavUtils;

public class MainActivity extends Activity {
	


	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_join_game);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		//getMenuInflater().inflate(R.menu.join_game, menu);
		return true;
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
	
    public void onClick(View v) {
    	
    	switch(v.getId()) {
    	case R.id.buttonJoin:
    		// User has attempted to join a game.
    		// Validate the input.
    		
    		EditText mEdit = (EditText)findViewById(R.id.gamePass);
    		
    		Log.i("join_button", "Join button was clicked.");
    		
    		if(mEdit.getText().toString().isEmpty() ||
    				mEdit.getText().toString().equalsIgnoreCase(getString(R.string.game_pass_string)) ) {
    			Log.i("join_button", "Join button text is empty.");
    			Toast.makeText(MainActivity.this, 
    					getString(R.string.toast_no_string_error), 
    					Toast.LENGTH_SHORT).show();
    			return; // Don't attempt to continue at this point.
    		}
    		
    		// Pass off to the loading activity.
    		Intent intent = new Intent(this, Loading.class);
    		intent.putExtra(Consts.GAME_PASSWORD, mEdit.getText().toString());
    		startActivity(intent);
    		
    		
    		
    		break; // Break for case R.id.buttonJoin
    	}
    	
    }

}
