#
# Functions for simplifying access to the pyevdev API
#

import re
import evdev
#
# Initialize evdev and attempt to find Card Reader Device
#
def initReader(vid, pid):
	devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	if not devices:
		print("No devices found.")
	reader = None
	for device in devices:
		if str(hex(device.info.vendor)[2:]) == vid:
			if str(hex(device.info.product)[2:]) == pid:
				print("USB Device {0}:{1} found".format(vid, pid))
				reader = device
			else:
				print("USB Device {0}:{1} not found".format(vid, pid))
	return reader

#
# Record all keyboard events until KEY_KPENTER is pressed
#
def readData(reader):
	keyEvents = []
	for event in reader.read_loop():
		if event.type == evdev.ecodes.EV_KEY:
			temp = evdev.categorize(event)
			if temp.keystate:
				keyEvents.append(temp)
				if keyEvents[-1].keycode == "KEY_KPENTER":
					break
	return keyEvents[:-1]

#
# Return a string of keys pressed from keyEvents list
#
### NOTE ###
# this seems to cover every card I could find but im not 200% sure.
def interpretEvents(keyEvents):
	if not keyEvents:
		return None
	resultString = ""
	modifier = False
	for event in keyEvents:
		if modifier:
			if event.keycode == "KEY_5":
				resultString += "%"
				modifier = False
				continue
			if event.keycode == "KEY_6":
				resultString += "^"
				modifier = False
				continue
			if event.keycode == "KEY_SLASH":
				resultString += "?"
				modifier = False
				continue
			if event.keycode == "KEY_EQUAL":
				resultString += "+"
				modifier = False
				continue
		if event.keycode == "KEY_LEFTSHIFT":
			modifier = True
			continue
		if event.keycode[-2] == "_":
			if str.isalnum(event.keycode[-1]):
				resultString += event.keycode[-1]
				continue
		if event.keycode == "KEY_SEMICOLON":
			resultString += ";"
			continue
		if event.keycode == "KEY_SPACE":
			resultString += " "
			continue
		if event.keycode == "KEY_EQUAL":
			resultString += "="
			continue
		raise KeyError("Undefined Key: " + event.keycode)
	return resultString

#
# Extract ID number from Card Data using preset regular expression
#
def extractID(data, regex):
	if regex:
		p = re.compile(regex)
		match = re.search(p, data)
		if not match:
			return None #not an ASU ID card
		if not match.group(1) == match.group(2):
			# lol wut
			return None #possibly corrupted ID.
		return match.group(1)