#!/usr/bin/python

import pyaudio
import wave
import time
import subprocess
import os.path
import json
import requests
import argparse
import webbrowser
import sys
import keyring
from rauth import OAuth1Service

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 6
SAVE_PATH = os.path.expanduser("~") + "/Music/recordings/"
WAVE_OUTPUT_FILENAME = "temp_{}.wav".format(int(time.time()))
COMPLETE_NAME = os.path.join(SAVE_PATH, WAVE_OUTPUT_FILENAME)

# Gracenote variables
CLIENT_ID = "YOUR-CLIENT-ID"
APP_PATH = "./sample"
LICENCE_PATH = "licence.txt"

# Discogs variables
DISCOGS_KEY = "key"
DISCOGS_SECRET = "secret"
DISCOGS_CONSUMER_KEY = "consumer_key"
DISCOGS_CONSUMER_SECRET = "consumer_secret"
DISCOGS_USERNAME = "username"

p = pyaudio.PyAudio()

class GracenoteError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

discogs = OAuth1Service(
    name="discogs",
    consumer_key=DISCOGS_CONSUMER_KEY,
    consumer_secret=DISCOGS_CONSUMER_SECRET,
    request_token_url="https://api.discogs.com/oauth/request_token",
    access_token_url="https://api.discogs.com/oauth/access_token",
    authorize_url="https://www.discogs.com/oauth/authorize",
    base_url="https://api.discogs.com/")

def discogs_get_master(artist_name, album_name):
    # TODO: sometimes comes up with nothing when it should find something
    payload = {
        "key": DISCOGS_KEY,
        "secret": DISCOGS_SECRET,
        "artist": artist_name,
        "release_title": album_name,
        "type": "master"
    }
    r = requests.get("https://api.discogs.com/database/search", params=payload)
    result = r.json()["results"]
    if len(result):
        return r.json()["results"][0]
    else:
        raise RuntimeError("No Discogs master found")

def discogs_get_release(master_id):
    release = requests.get("https://api.discogs.com/masters/"+str(master_id)+"/versions",
        params={"per_page": 1}
        )
    return release.json()["versions"][0]

def discogs_get_oauth_session():
    access_token = keyring.get_password("system", "access_token")
    access_token_secret = keyring.get_password("system", "access_token_secret")

    if access_token and access_token_secret:
        session = discogs.get_session((access_token, access_token_secret))
    else:
        request_token, request_token_secret = discogs.get_request_token()
        authorize_url = discogs.get_authorize_url(request_token)
        webbrowser.open(authorize_url, new=2, autoraise=True)
        print "To enable Discogs access, visit this URL in your browser: "+authorize_url
        oauth_verifier = raw_input("Enter key: ")
        session = discogs.get_auth_session(request_token, request_token_secret,
            method="POST",
            data={"oauth_verifier": oauth_verifier})
        keyring.set_password("system", "access_token", session.access_token)
        keyring.set_password("system", "access_token_secret", session.access_token_secret)
    return session

def discogs_add_wantlist(session, username, release_id):
    r = session.put("https://api.discogs.com/users/"+username+"/wants/"+str(release_id),
        header_auth=True,
        headers={
            "content-type": "application/json",
            "user-agent": "identify-audio-v0.2"})
    return r.status_code

def find_device(device_sought, device_list):
    for device in device_list:
        if device["name"] == device_sought:
            return device["index"]
    raise KeyError("Device {} not found.".format(device_sought))

def get_device_list():
    num_devices = p.get_device_count()
    device_list = [p.get_device_info_by_index(i) for i in range(0, num_devices)]
    return device_list

def get_soundflower_index():
    device_list = get_device_list()
    soundflower_index = find_device("Soundflower (2ch)", device_list)
    return soundflower_index

def get_current_output():
    device_list = get_device_list()
    try:
        find_device("USB Audio Device", device_list)
        return "USB Audio Device"
    except:
        return "Built-in Output"

def get_multi_device(output):
    if output == "USB Audio Device":
        return "Multi-Output Device (USB)"
    else:
        return "Multi-Output Device (Built-in)"

def record_audio(device_index, format, channels, rate, chunk, record_seconds):
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=chunk)

    print ("Recording for {} seconds...".format(record_seconds))

    frames = []

    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    return frames

def write_file(frames, path, format, channels, rate):
    wf = wave.open(path, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()

    return path

def query_gracenote(sound_path):
    out = subprocess.check_output([APP_PATH, CLIENT_ID.split("-")[0],
        CLIENT_ID.split("-")[1], LICENCE_PATH, sound_path])
    result = json.loads(out)
    if result["error"]:
        raise GracenoteError(result["error"])
    return result

def main():

    parser = argparse.ArgumentParser(description="Identify currently playing audio")
    parser.add_argument("--discogs", "-d", action="store_true")
    parser.add_argument("--want", "-w", action="store_true")
    parser.add_argument("--open", "-o", action="store_true")
    args = vars(parser.parse_args())

    output = get_current_output()
    multi_out = get_multi_device(output)

    if subprocess.call(["SwitchAudioSource", "-s", multi_out]) == 0:
        length = RECORD_SECONDS
        match = False
        attempts = 0
        while not match and attempts <= 2:
            input_audio = record_audio(get_soundflower_index(), FORMAT, CHANNELS, RATE, CHUNK, length)
            try:
                write_file(input_audio, COMPLETE_NAME, FORMAT, CHANNELS, RATE)
            except IOError:
                print "Error writing the sound file."
            resp = query_gracenote(COMPLETE_NAME)
            if resp["result"] == None:
                print "The track was not identified."
                length += 3
                attempts += 1
                if attempts <=2:
                    print "Retrying..."
            else:
                print json.dumps(resp["result"], indent=4, separators=(""," - "), ensure_ascii=False).encode("utf8")
                match = True
    if match:
        if args["discogs"] or args["want"]:
            try:
                master = discogs_get_master(resp["result"]["artist_name"], resp["result"]["album_name"])
                if not args["want"]:
                    want_add = raw_input("Add this to your Discogs wantlist? y/n: ")
                if want_add == "y" or args["want"]:
                    release = discogs_get_release(master["id"])
                    session = discogs_get_oauth_session()
                    status = discogs_add_wantlist(session, DISCOGS_USERNAME, release["id"])
                    if status == 201:
                        print "Added '{}' to your Discogs wantlist".format(release["title"])
                    else:
                        print "Error code {} adding the release to your Discogs wantlist".format(status)
                else:
                    url = "https://discogs.com" + master["uri"]
                    print "Find online: " + url
                    if args["open"]:
                        webbrowser.open(url, new=2, autoraise=True)
            except RuntimeError:
                print "No matching Discogs master release could be found"
    else:
        raise RuntimeError("Couldn't switch to multi-output device.")
    p.terminate()
    os.remove(COMPLETE_NAME)
    if subprocess.call(["SwitchAudioSource", "-s", output]) == 0:
        return
    else:
        raise RuntimeError("Couldn't switch back to output.")

if __name__ == "__main__":
    try:
        main()
    except GracenoteError as e:
        print "Gracenote error: "+e.value
        sys.exit(1)
    except Exception as e:
        print e
        sys.exit(1)
