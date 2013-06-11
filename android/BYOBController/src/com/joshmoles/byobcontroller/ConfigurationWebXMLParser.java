/**
 * Project: ECE 544 Final Project
 * Primary Author: Josh Moles
 * Teammates: Dimitriy A. Labunsky, Tejashree Chaudhari, Tejas Tapsale
 *
 * Demonstration Date: June 11, 2013
 * 
 * Description: Class to parse XML configuration received from the server.
 * Based off example from: http://developer.android.com/training/basics/network-ops/xml.html
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

import java.io.IOException;
import java.io.InputStream;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import android.os.Parcel;
import android.os.Parcelable;
import android.util.Xml;

public class ConfigurationWebXMLParser {
	
	private final String ns = null;
	
	// Class to hold the configuration read from web site.
	public static class ConfigEntry implements Parcelable{
		
		// Constants for where items are in array.
		public final String pubnubSubscribe;
		public final String pubnubPublish;
		public final String pubnubSecret;
		
		private ConfigEntry(String pubnubSubscribe, 
				String pubnubPublish, 
				String pubnubSecret) {
			this.pubnubSubscribe = pubnubSubscribe;
			this.pubnubPublish   = pubnubPublish;
			this.pubnubSecret    = pubnubSecret;
		}
			
		 public int describeContents() {
		     return 0;
		 }
		
		 public void writeToParcel(Parcel out, int flags) {
			 out.writeStringArray(new String[] {this.pubnubSubscribe,
					 this.pubnubPublish,
					 this.pubnubSecret});
		 }
		
		 public static final Parcelable.Creator<ConfigEntry> CREATOR 
		 	= new Parcelable.Creator<ConfigEntry>() {
		     public ConfigEntry createFromParcel(Parcel in) {
		         return new ConfigEntry(in);
		     }
		
		     public ConfigEntry[] newArray(int size) {
		         return new ConfigEntry[size];
		     }
		 };
		
		 private ConfigEntry(Parcel in) {
		    String[] data = new String[3];
		    in.readStringArray(data);
		    
			this.pubnubSubscribe = data[0];
			this.pubnubPublish   = data[1];
			this.pubnubSecret    = data[2];
		 }
		
	}
	
	
	public ConfigEntry parse(InputStream in) throws XmlPullParserException, IOException {
		try {
			XmlPullParser parser = Xml.newPullParser();
			parser.setFeature(XmlPullParser.FEATURE_PROCESS_NAMESPACES, false);
			parser.setInput(in, null);
			parser.nextTag();
			return readConfig(parser);
		} finally {
			in.close();
		}
	}
	
	private ConfigEntry readConfig(XmlPullParser parser) throws XmlPullParserException, IOException {

	    parser.require(XmlPullParser.START_TAG, ns, "configuration");
	    String pubnubSubscribe = "";
	    String pubnubPublish = "";
	    String pubnubSecret = "";
	    while (parser.next() != XmlPullParser.END_TAG) {
	        if (parser.getEventType() != XmlPullParser.START_TAG) {
	            continue;
	        }
	        String name = parser.getName();
	        if (name.equals("pubnub_pub")) {
	        	pubnubPublish = readPubNub(parser, name);
	        } else if (name.equals("pubnub_sub")) {
	        	pubnubSubscribe = readPubNub(parser, name);
	        } else if (name.equals("pubnub_sec")) {
	        	pubnubSecret = readPubNub(parser, name);
	        } else {
	            skip(parser);
	        }
	    }
	    return new ConfigEntry(pubnubSubscribe, pubnubPublish, pubnubSecret);
	}

	// Processes pubnub tags in the feed.
	private String readPubNub(XmlPullParser parser, String name) throws IOException, XmlPullParserException {
	    parser.require(XmlPullParser.START_TAG, ns, name);
	    String title = readText(parser);
	    parser.require(XmlPullParser.END_TAG, ns, name);
	    return title;
	}
	
	// Extract values for the pubNub keys
	private String readText(XmlPullParser parser) throws IOException, XmlPullParserException {
	    String result = "";
	    if (parser.next() == XmlPullParser.TEXT) {
	        result = parser.getText();
	        parser.nextTag();
	    }
	    return result;
	}
	    
	    
    private void skip(XmlPullParser parser) throws XmlPullParserException, IOException {
        if (parser.getEventType() != XmlPullParser.START_TAG) {
            throw new IllegalStateException();
        }
        int depth = 1;
        while (depth != 0) {
            switch (parser.next()) {
            case XmlPullParser.END_TAG:
                depth--;
                break;
            case XmlPullParser.START_TAG:
                depth++;
                break;
            }
        }
     }

}
