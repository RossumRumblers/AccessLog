import sys
import evdev

def initReader(vid, pid):
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    if not devices:
        print("No devices found, please try re-running the script as root.")
    reader = None
    for device in devices:
        if str(hex(device.info.vendor)[2:]) == vid:
            if str(hex(device.info.product)[2:]) == pid:
                reader = device
    return reader

def readData(reader):
    keyEvents = []
    for event in reader.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            temp = evdev.categorize(event)
            if temp.keystate:
                keyEvents.append(temp)
                #print(keyEvents[-1].keycode)
                if keyEvents[-1].keycode == "KEY_KPENTER":
                    break
    return keyEvents[:-1]

def interpretEvents(keyEvents):
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

def extractID(data, regex):
    if regex:
        p = re.compile(regex)
        match = re.search(p, data)
        if not match:
            return None #not an ASU ID card
        if not match.group(1) == match.group(2):
            # lol wut
            print("possibly corrupted ID?")
            return None
        return match.group(1)

if __name__ == '__main__':
    import re
    regex = ";601744(\d{10})1(\d{10})\?"
    cardReader = initReader("5131","2007")
    if not cardReader:
        print("card Reader not found.")
    cardReader.grab()
    data = interpretEvents(readData(cardReader))
    cardReader.ungrab()
    print(extractID(data, regex))

    
