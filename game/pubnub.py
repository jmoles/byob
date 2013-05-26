import sys
import threading
import time
import random
import string
from yaml import load
from lib.Pubnub import Pubnub

# Import the YAML Stuff
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

# Attempt to read the yaml configuration
yaml_config_file = open('../config.yml', 'r')
config_data      = load(yaml_config_file)

## Build the class
pubnub = Pubnub(
    config_data["pubnub"]["publish"],  ## PUBLISH_KEY
    config_data["pubnub"]["sub"],  ## SUBSCRIBE_KEY
    config_data["pubnub"]["secret"],    ## SECRET_KEY
    False    ## SSL_ON?
)

print("My UUID is: " + pubnub.uuid)

channel = ''.join("player_control")

## Subscribe Example
def receive(message) :
    print(message)
    return False


try:
	while 1:
	    print("Listening for messages on '%s' channel..." % channel)
	    pubnub.subscribe({
	        'channel'  : channel,
	        'callback' : receive 
	    })
except KeyboardInterrupt:
	pass