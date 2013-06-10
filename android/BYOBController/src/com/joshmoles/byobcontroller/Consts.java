package com.joshmoles.byobcontroller;

public interface Consts {
	
    public static final String PUBNUB_CHANNEL 		= "player_control";
	
    public static final String BASE_URL 			= "http://byob.joshmoles.com";
    
    public static final int XML_FETCH_TIMEOUT 		= 10000;
    
    // Length of vibration on button presses in game
    public static final int VIBE_LENGTH				= 20;
   
	// Strings used in logging information
	public final static String LOAD_FETCH    		= "load_fetch";
	public final static String CONTROL_AREA  		= "control_area";
	
	// Prefixes for channels in Pubnub
	public final static String LOBBY_PREFIX  		= "lobby-";
	public final static String GAME_PREFIX  		= "game-";
	
	// Messages from Pubnub
	public final static String PUBNUB_RESP_GAMEFULL = "game-is-full";
	public final static String PUBNUB_RESP_GAMERDY  = "join-game";
	public final static String PUBNUB_RESP_GAMEOVER = "game-over";
	public final static String PUBNUB_RESP_WINNER   = "game-winner";
	public final static String PUBNUB_RESP_LOSER    = "game-loser";
	
    // Constant path to send between intents
	public final static String GAME_PASSWORD 		= "com.joshmoles.byobcontroller.GAME_PASS";
	public final static String CONFIG_OBJ    		= "com.joshmoles.byobcontroller.CONFIG_OBJ";

}
