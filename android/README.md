Android
=======

The Android software for controlling the game goes in this folder.

Configuration
-------------
Configuration for Pubnub is required. Strings need to get defined as an android resource. For example, creating a file called app_config.xml in values with the following would work:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="publish_key">PUBLISH KEY HERE</string>
    <string name="subscribe_key">SUBSCRIBE KEY HERE</string>
    <string name="secret_key">SECERT KEY HERE (Optional)</string>
    
</resources>

```
