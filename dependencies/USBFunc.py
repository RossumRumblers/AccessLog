'''
Functions for simplifying access to the pyevdev API
'''

import re
import evdev

def initReader(vid, pid):
    '''
    Initialize evdev and attempt to find Card Reader Device
    '''
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    if not devices:
        print("No devices found.")
        return None

    reader = None
    for device in devices:
        if str(hex(device.info.vendor)[2:]) == vid:
            if str(hex(device.info.product)[2:]) == pid:
                print("USB Device {0}:{1} found".format(vid, pid))
                reader = device
            else:
                print("USB Device {0}:{1} not found".format(vid, pid))
    return reader

def readData(reader):
    '''
    Record all keyboard events until KEY_KPENTER is pressed
    '''
    keyEvents = []
    for event in reader.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            temp = evdev.categorize(event)
            if temp.keystate:
                keyEvents.append(temp)
                if keyEvents[-1].keycode == "KEY_KPENTER":
                    break
    return keyEvents[:-1]


def interpretEvents(keyEvents):
    '''
    Return a string of keys pressed from keyEvents list

    NOTE:
        this seems to cover every card I could find but I'm not 200% sure.
    '''
    if not keyEvents:
    # don't do anything on empty array
        return None

    resultString = ""
    modifier = False

    for event in keyEvents:
    #iterate through keyEvent List

        if modifier:
            # Modifier is used to indicate special character typing.
            # As we must interpret keyEvents, if you want to type a percent sign '%'
            #  we have to press the Shift Key which is what modifier indicates
            if event.keycode == "KEY_5":
                resultString += "%"
            elif event.keycode == "KEY_6":
                resultString += "^"
            elif event.keycode == "KEY_SLASH":
                resultString += "?"
            elif event.keycode == "KEY_EQUAL":
                resultString += "+"
            else:
                #I don't think it means keyboard key...but I also don't care
                raise KeyError("Undefined Key: " + event.keycode)
        else:
            # I think the card reader only uses left shift but just in case, check both
            if event.keycode == "KEY_LEFTSHIFT" or event.keycode == "KEY_RIGHTSHIFT":
                modifier = True
                continue
            elif event.keycode[-2] == "_":
                # if the second to last character is an underscore then the keycode is
                #  a single character (KEY_A) so doublecheck that it is alpha-numeric
                #  and just push it
                if str.isalnum(event.keycode[-1]):
                    resultString += event.keycode[-1]
                else:
                    raise KeyError("Undefined Key: " + event.keycode)
            elif event.keycode == "KEY_SEMICOLON":
                resultString += ";"
            elif event.keycode == "KEY_SPACE":
                resultString += " "
            elif event.keycode == "KEY_EQUAL":
                resultString += "="
            else:
                raise KeyError("Undefined Key: " + event.keycode)
    return resultString

def extractID(data, regex):
    '''
    Extract ID number from Card Data using preset regular expression
    '''
    if regex and data:
        # maybe I'ma little too cautious sometimes...
        p = re.compile(regex)
        match = re.search(p, data)
        if not match:
            # Not a recognized card
            return None
        return match.group(1)
