/**
 * Project: ECE 544 Final Project
 * Primary Author: Josh Moles
 * Teammates: Dimitriy A. Labunsky, Tejashree Chaudhari, Tejas Tapsale
 *
 * Demonstration Date: June 11, 2013
 * 
 * Description: Class to aid in download of configuration information.
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

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import org.xmlpull.v1.XmlPullParserException;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;

import com.joshmoles.byobcontroller.ConfigurationWebXMLParser.ConfigEntry;

public class DownloadWebPageTask extends AsyncTask<String, Void, ConfigEntry>{
	
	Context context;
	
	Exception storedE = null;
	
	public DownloadWebPageTask(Context context) {
		this.context = context.getApplicationContext();
		
	}

	/*
	 * (non-Javadoc)
	 * @see android.os.AsyncTask#doInBackground(Params[])
	 * Attempts to fetch the XML data and parse into config object.
	 */
	@Override
	protected ConfigurationWebXMLParser.ConfigEntry doInBackground(String... urls) {
		ConfigEntry myConfig = null;
		InputStream is = null;
		
		try {
			try {
				is =  loadXmlFromNetwork(urls[0]);
			} catch (FileNotFoundException e) {
				Log.w(Consts.LOAD_FETCH, "404 on password!");
				storedE = e;
				this.cancel(true);
			}
			Log.d(Consts.LOAD_FETCH, "At post HTTP fetch.");
			
		    // Instantiate the parser
		    ConfigurationWebXMLParser configParser = new ConfigurationWebXMLParser();
		    
		    Log.d(Consts.LOAD_FETCH, "XML Parsing worked");
		    
		    try {
				myConfig = configParser.parse(is);
			} catch (XmlPullParserException e) {
				// TODO Auto-generated catch block
				storedE = e;
				e.printStackTrace();
				return null;
			}  catch (IOException e) {
				storedE = e;
				// TODO Auto-generated catch block
				e.printStackTrace();
				return null;
			} 
		    
		    // If we get here, myConfig Parser succeeded.
		    Log.d(Consts.LOAD_FETCH, "Done with doInbackground.");
			
		} catch (IOException e) {
			storedE = e;
			e.printStackTrace();
			this.cancel(true);
			return null;
		} catch (XmlPullParserException e) {
			storedE = e;
			e.printStackTrace();
			this.cancel(true);
			return null;
		}
		
		return myConfig;
	}
	
	@Override
	protected void onPostExecute(ConfigEntry result) {
		
		Log.d(Consts.LOAD_FETCH, "Inside onPostExecute!");
		
		if(storedE == null && !this.isCancelled() && result != null) {
			
			return;
			
		} else {
			Log.e(Consts.LOAD_FETCH, "onPostExecute did not finish!");
			this.cancel(true);

		}
		
	}
	
	// Fetches XML data as a string from the web server.
	private InputStream loadXmlFromNetwork(String urlString)
			throws XmlPullParserException, IOException {
		return downloadUrl(urlString);
	}

	// Given a string representation of a URL, sets up a connection and gets
	// an input stream.
	private InputStream downloadUrl(String urlString) throws IOException {
	    URL url = new URL(urlString);
	    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
	    conn.setReadTimeout(10000 /* milliseconds */);
	    conn.setConnectTimeout(15000 /* milliseconds */);
	    conn.setRequestMethod("GET");
	    conn.setDoInput(true);
	    // Starts the query
	    conn.connect();
	    return conn.getInputStream();
	}
}

