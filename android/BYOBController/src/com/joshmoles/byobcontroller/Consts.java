/**
 * Project: ECE 544 Final Project
 * Primary Author: Josh Moles
 * Teammates: Dimitriy A. Labunsky, Tejashree Chaudhari, Tejas Tapsale
 *
 * Demonstration Date: June 11, 2013
 * 
 * Description: Constants for this project
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
	
	// Message to send on Pubnub
	public final static String PUBNUB_SEND_GOODBYE  = "goodbye";
	
    // Constant path to send between intents
	public final static String GAME_PASSWORD 		= "com.joshmoles.byobcontroller.GAME_PASS";
	public final static String CONFIG_OBJ    		= "com.joshmoles.byobcontroller.CONFIG_OBJ";

}
