Identify audio playing on your computer
=======================================

This script can identify any audio playing on your computer. It's useful if you're listening to a mix and want to identify a track without having to use a phone to Shazam your computer's output. Your music will continue playing while it's working. It relies on Gracenote to fingerprint and identify the track. It has integration with Discogs if you want to find the release online.

Dependencies
------------

This script requires:

* Python and PyAudio to record the audio.
* [Soundflower](https://github.com/mattingalls/Soundflower) to capture audio output into an input PyAudio can use.
* [SwitchAudioSource](https://github.com/deweller/switchaudio-osx) to programmatically switch between audio devices.

Installation for OS X 64 bit
---------------------

1. Make sure PyAudio, Soundflower and SwitchAudioSource are installed.  

2. In Audio MIDI settings, create a multi-output device. The master device should be "Soundflower (2ch)" and it should use "Soundflower (2ch)" and "Built-in Output". This will allow the script to listen to the audio through the Soundflower device while you continue to hear it through the computer's output. Name the multi-output device "Multi-Output Device (Built-in)" by double-clicking on the name. The script will look for a device with this exact name.  

3. If you use headphones they will work with the multi-output device you've just made. However, if you also use a USB audio device you'll need to create another multi-output device, this time using "USB Audio Device" rather than "Built-in Output". Call it "Multi-Output Device (USB)" so that the script can pick it up.
4. Make sure the executable and dylib files together in a directory. 

5. The script will look for configuration details in a .identifyaudio.rc file in your home directly (by default). You can edit the script to provide the details in the script itself or create the configuration file with the following format:  

> APP_PATH /path/to/sample/executable  
> DISCOGS_KEY your_details  
> DISCOGS_SECRET your_details  
> DISCOGS_CONSUMER_KEY your_details  
> DISCOGS_CONSUMER_SECRET your_details  
> DISCOGS_USERNAME your_user_name  
> DISCOGS_REQUEST_TOKEN_URL https://api.discogs.com/oauth/request_token  
> DISCOGS_ACCESS_TOKEN_URL https://api.discogs.com/oauth/access_token  
> DISCOGS_AUTHORIZE_URL https://www.discogs.com/oauth/authorize  
> DISCOGS_BASE_URL https://api.discogs.com/  

(that's the name followed by a single space followed by the value followed by a newline).  

8. You can also change the directory to which the script will write temp files. By default it's ~/Music/temp. The script will delete files once it's used them in any case.  

9. If you do not have OS X 64-bit you will need to recompile the executable using the Gracenote SDK (it's free).  

10. If you're better at compiling than me it would be great to have a single executable.  

Usage
-----

When you are playing a track you want to identify, just type `python identify.py` from the directory. It will try a few times to identify the track and give the album and track names if it finds them.  

To make the script available from anywhere in the console, move "identify.py" to "/usr/local/bin", or add its current directory to your path. This will mean you can just use `identify.py` without having to be in a particular directory or type `python`.

Flags
=====

The `--discogs|-d` flag enables Discogs lookup. It can be combined with `--want|-w` to automatically add the release to your want list or `--open|-o` to open the release's Discogs page in your webbrowser. You will need to authorise the app the first time you want to make changes to your want list.  

It also has a `--quiet|-q` flag to only output matches in JSON format, for use in pipelines, and `--verbose|-v` to get tracebacks.
