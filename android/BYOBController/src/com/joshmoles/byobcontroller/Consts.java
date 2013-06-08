package com.joshmoles.byobcontroller;

public interface Consts {
	
    public static final String PUBNUB_CHANNEL = "player_control";
	
    public static final String BASE_URL = "http://byob.joshmoles.com";
    
    public static final int XML_FETCH_TIMEOUT = 10000;
   
	// Strings used in logging information
	public final static String LOAD_FETCH = "load_fetch";
	
    // Constant path to send between intents
	public final static String GAME_PASSWORD = "com.joshmoles.byobcontroller.GAME_PASS";
	public final static String PUBNUB_OBJ    = "com.joshmoles.byobcontroller.PUBNUB_OBJ";

}
