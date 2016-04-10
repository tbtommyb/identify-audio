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

Installation for OS X
---------------------

1. Make sure PyAudio, Soundflower and SwitchAudioSource are installed.
2. In Audio MIDI settings, create a multi-output device. The master device should be "Soundflower (2ch)" and it should use "Soundflower (2ch)" and "Built-in Output". This will allow the script to listen to the audio through the Soundflower device while you continue to hear it through the computer's output. Name the multi-output device "Multi-Output Device (Built-in)" by double-clicking on the name. The script will look for a device with this exact name.
3. If you use headphones they will work with the multi-output device you've just made. However, if you also use a USB audio device you'll need to create another multi-output device, this time using "USB Audio Device" rather than "Built-in Output". Call it "Multi-Output Device (USB)" so that the script can pick it up.
3. Register for a Gracenote Web API account and download their SDK.
5. Replace "samples/musicid_stream/main.c" in the SDK with the "main.c" in this repository. The only difference is that the updated version takes the sound file as a command line a
rgument. Before building it you will need to put in the directory the header and link files for your architecture (from "/lib/" and "/include" in the SDK directory). 64bit users need to use `make ARCH=x86_64`.
6. Create a "licence.txt" file containing the licence information provided in your online Gracenote account.
7. In the script there are a couple of user-defined details for the Gracenote API. Fill in your details. It's easiest to keep the sample executable and licence.txt in the same directory but it's up to you. You will need the architecture-appropriate library and header files in the directory with the executable.
8. You can also change the directory to which the script will write temp files. By default it's ~/Music/temp. The script will delete files once it's used them in any case.
9. When you are playing a track you want to identify, just type "python identify.py" from the directory. It will try a few times to identify the track and give the album and track names if it finds them.
10. To make the script available from anywhere in the console, move "identify.py" to "/usr/local/bin". You'll need to update the paths to the Gracenote executable and licence.txt files.
