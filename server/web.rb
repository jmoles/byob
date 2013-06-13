require 'builder'
require 'logger'
require 'sinatra'
require 'pubnub'

COLORS = { 	"white"     => [255, 255, 255], 
			"black"     => [  0,   0,   0],
			"red"       => [255,   0,   0],
			"green"     => [  0, 255,   0],
			"darkgreen" => [  0, 155,   0], 
			"darkgray"  => [ 40,  40,  40],
			"yellow"    => [255, 255,   0],
			"blue"      => [  0,   0, 255],
			"cyan"      => [  0, 255, 255],
			"lime"      => [  0, 255,   0],
			"gray"      => [128, 128, 128],
			"silver"    => [192, 192, 192],
			"purple"    => [128,   0, 128],
			"olive"     => [128, 128,   0],
			"navy"      => [0  ,   0, 128],
			"maroon"    => [128,   0,   0] }

pubnub = Pubnub.new(
    :publish_key   => ENV['PUBNUB_PUBLISH'], # publish_key only required if publishing.
    :subscribe_key => ENV['PUBNUB_SUBSCRIBE'], # required
    :secret_key    => nil,    # optional, if used, message signing is enabled
    :cipher_key    => nil,    # optional, if used, encryption is enabled
    :ssl           => nil     # true or default is false
)


def configuration_xml
	xml = Builder::XmlMarkup.new( :indent => 2)
	xml.instruct! :xml, :encoding => "ASCII"
	xml.configuration do |p|
		p.pubnub_pub ENV['PUBNUB_PUBLISH']
		p.pubnub_sub ENV['PUBNUB_SUBSCRIBE']
		p.pubnub_sec ""
		p.max_players 4
		p.num_rounds 3
		xml.colors do |c|
			COLORS.each do |k, v|
				c.color(v, :"name" => k)
			end
		end
		xml.strings do |s|
			s.string("BYOB",			:"id" => "game_name")
			s.string("game-is-full", 	:"id" => "game_full")
			s.string("join-game", 		:"id" => "game_join")
			s.string("lobby_", 			:"id" => "lobby_prefix")
			s.string("up", 				:"id" => "up_button")
			s.string("down", 			:"id" => "down_button")
			s.string("left", 			:"id" => "left_button")
			s.string("right", 			:"id" => "right_button")
			s.string("A", 				:"id" => "a_button")
			s.string("B", 				:"id" => "b_button")
		end
	end
end

get '/' do
	"Hello, world!"
end

get '/client/getconfig/' + ENV['GAME_PASS'] do
	content_type 'text/xml'
	configuration_xml
end
