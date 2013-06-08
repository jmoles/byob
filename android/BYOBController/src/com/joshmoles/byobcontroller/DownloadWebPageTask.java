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
			Log.i(Consts.LOAD_FETCH, "At post HTTP fetch.");
			
		    // Instantiate the parser
		    ConfigurationWebXMLParser configParser = new ConfigurationWebXMLParser();
		    
		    Log.i(Consts.LOAD_FETCH, "XML Parsing worked");
		    
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
		    Log.i(Consts.LOAD_FETCH, "Done with doInbackground.");
			
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

