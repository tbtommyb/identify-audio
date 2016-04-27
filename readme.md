Identify audio playing on your computer
=======================================

This script can identify any audio playing on your computer. It's useful if you're listening to a mix and want to identify a track without having to use a phone to Shazam your computer's output. Your music will continue playing while it's working.

Dependencies
------------

This script requires:

* Python and PyAudio to record the audio.
* [Soundflower](https://github.com/mattingalls/Soundflower) to capture audio output into an input PyAudio can use.
* [SwitchAudioSource](https://github.com/deweller/switchaudio-osx) to programmatically switch between audio devices.
* A [Gracenote Web API account](https://developer.gracenote.com/web-api) (it's free) and some files from their [SDK](https://developer.gracenote.com/gnsdk) in order to identify the recorded audio.
* OR, if you are using OS X 64-bit, you should be able to use the executable in the 'build' directly without needing to create a Gracenote account.

Installation for OS X
---------------------

1. Make sure PyAudio, Soundflower and SwitchAudioSource are installed.
2. In Audio MIDI settings, create a multi-output device. The master device should be "Soundflower (2ch)" and it should use "Soundflower (2ch)" and "Built-in Output". This will allow the script to listen to the audio through the Soundflower device while you continue to hear it through the computer's output. Name the multi-output device "Multi-Output Device (Built-in)" by double-clicking on the name. The script will look for a device with this exact name.
3. If you use headphones they will work with the multi-output device you've just made. However, if you also use a USB audio device you'll need to create another multi-output device, this time using "USB Audio Device" rather than "Built-in Output". Call it "Multi-Output Device (USB)" so that the script can pick it up.
4. Register for a Gracenote Web API account and download their SDK.
5. Replace "samples/musicid_stream/main.c" in the SDK with the "main.c" in this repository. It has been changed to output in JSON and take a file input. Before building it you will need to put in the directory the header and link files for your architecture (from "/lib/" and "/include" in the SDK directory). 64bit users need to use `make ARCH=x86_64`, or can just use the executable files in the 'build' directory. If you do so, providing your own Gracenote IDs is optional (though you'll still need to provide the licence file, below). Be sure to keep the dylib files in the same directory.
6. Create a "licence.txt" file containing the licence information provided in your online Gracenote account.
7. The script will look for configuration details in a .identifyaudio.rc file in your home directly (by default). You can edit the script to provide the details in the script itself or create the configuration file with the following format:
APP_PATH /path/to/sample/executable  
LICENCE_PATH /path/to/licence.txt  
CLIENT_ID Gracenote_client_id  
DISCOGS_KEY your_details  
DISCOGS_SECRET your_details  
DISCOGS_CONSUMER_KEY your_details  
DISCOGS_CONSUMER_SECRET your_details  
DISCOGS_USERNAME your_user_name  
DISCOGS_REQUEST_TOKEN_URL https://api.discogs.com/oauth/request_token  
DISCOGS_ACCESS_TOKEN_URL https://api.discogs.com/oauth/access_token  
DISCOGS_AUTHORIZE_URL https://www.discogs.com/oauth/authorize  
DISCOGS_BASE_URL https://api.discogs.com/
(that's the name followed by a single space followed by the value followed by a newline).
8. You can also change the directory to which the script will write temp files. By default it's ~/Music/temp. The script will delete files once it's used them in any case.
9. When you are playing a track you want to identify, just type `python identify.py` from the directory. It will try a few times to identify the track and give the album and track names if it finds them.
10. The `--discogs|-d` flag enables Discogs lookup. It can be combined with `--want|-w` to automatically add the release to your want list or `--open|-o` to open the release's Discogs page. You will need to authorise the app the first time you want to make changes to your want list. It also has a `--quiet|-q` flag to only output matches in JSON format, for use in pipelines, and `--verbose|-v` to get tracebacks.
11. To make the script available from anywhere in the console, move "identify.py" to "/usr/local/bin".
