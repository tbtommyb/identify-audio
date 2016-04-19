#!/usr/bin/python

import pyaudio
import wave
import time
import subprocess
import os.path
import json

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

p = pyaudio.PyAudio()

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
	return json.loads(out)

def main():
	output = get_current_output()
	multi_out = get_multi_device(output)

	if subprocess.call(["SwitchAudioSource", "-s", multi_out]) == 0:
		length = RECORD_SECONDS
		attempts = 0
		while True:
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
				if attempts == 3:
					break
				print "Retrying..."
			else:
				print json.dumps(resp["result"], indent=4, separators=(""," - "))
				break
	else:
		raise RuntimeError("Couldn't switch to multi-output device.")
	p.terminate()
	os.remove(COMPLETE_NAME)
	if subprocess.call(["SwitchAudioSource", "-s", output]) == 0:
	 	return
	else:
	 	raise RuntimeError("Couldn't switch back to output.")

if __name__ == "__main__":
	main()
