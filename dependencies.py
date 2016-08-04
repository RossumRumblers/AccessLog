#
# A file to simply basic functions for later Use
# the functions include those form the API and pyevdev
#

import os
import re
import sys
import evdev
import httplib2
import oauth2client

from oauth2client import tools
from oauth2client import client
from apiclient import discovery

#
# Exception Classes
#
class NoValueReturnedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidInputTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RangeNotUpdatedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#
# Test Root Access
# This function will not prompt and ask for root, only check and return True or False
#
def testRoot():
    p = subprocess.Popen('sudo -n echo', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    retval = p.stdout.readlines()[0].find("sudo: a password is required") == -1
    wait = p.wait()
    return retval


#
# Retrieve Access Ceredentials
#
def getCredentials(CRED_File, Secret_FileName, Scopes, APPLICATION_NAME, rebuild):
    # Attempt to retreieve credentials from file
    store = oauth2client.file.Storage(CRED_File)
    credentials = store.get()
    if not credentials or credentials.invalid or rebuild:
        # Get Credentials from server using Client keys
        flow = client.flow_from_clientsecrets(Secret_FileName, Scopes)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + CRED_File)
    return credentials

#
# Create API Service for acccessing spreadsheets
#
def createAPIService(credentials, discoveryUrl):
    http = credentials.authorize(httplib2.Http())
    if not http:
        print("Authorization Failed. Terminating.")
        sys.exit()
    print("Authorization Successful.")
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    if not service:
        print("Service Creation Failed. Terminating.")
        sys.exit()
    print("Service Creation Succeeded.")
    return service

#
# Request Range via get command
#
def requestRange(service, SpreadsheetId, range):
    returnedRange = service.spreadsheets().values().get(spreadsheetId=SpreadsheetId, range=range).execute()
    values = returnedRange.get('values', [])
    if not values:
        raise NoValueReturnedError(range)
    else:
        return values

#
# Request Range via batchGet command
#
def requestRanges(service, SpreadsheetId, ranges):
    result = []
    returnedRanges = service.spreadsheets().values().batchGet(spreadsheetId=SpreadsheetId, ranges=ranges).execute()
    values = returnedRanges.get('valueRanges', [])
    if not values:
        raise NoValueReturnedError(ranges)
    else:
        for elem in values:
            result.append(elem.get('values', []))
        return result

def updateRange(service, SpreadsheetId, range, sheetData, inputType):
    requestBody = {'values': sheetData}
    if inputType in ['RAW', 'USER_ENTERED']:
        returnedRange = service.spreadsheets().values().update(spreadsheetId=SpreadsheetId, range=range, body=requestBody, valueInputOption=inputType).execute()
        if not returnedRange:
            raise RangeNotUpdatedError(valueRange)
    else:
        raise InvalidInputTypeError(ranges)
    return returnedRange

def updateRanges(service, SpreadsheetId, JSONrequest):
    """
    function currently broken
    https://developers.google.com/sheets/reference/rest/v4/spreadsheets/request#Request
    """ 
    valueRanges = []
    for array in sheetData:
        ranges.append({'values': array})
    requestBody = {'data': ranges}
    print(requestBody)
    if inputType in ['RAW', 'USER_ENTERED']:
        returnedRange = service.spreadsheets().values().batchUpdate(spreadsheetId=SpreadsheetId, body=requestBody).execute()
        if not returnedRange:
            raise RangeNotUpdatedError(valueRange)
    else:
        raise InvalidInputTypeError(ranges)
    return returnedRange

def autoResizeRange(service, SpreadsheetId, range, dimension):
    """
    function currently broken
    """ 
    requestBody = {
        'requests': [{
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": SpreadsheetId,
                        "dimension": enum(Dimension),
                        "startIndex": number,
                        "endIndex": number,
                    }
                }
            }
        ],
    }
    if inputType in ['ROWS', 'COLUMNS']:
        returnedRange = service.spreadsheets().values().update(spreadsheetId=SpreadsheetId, range=range, body=requestBody, valueInputOption=inputType).execute()
        if not returnedRange:
            raise RangeNotUpdatedError(valueRange)
    else:
        raise InvalidInputTypeError(ranges)
    return returnedRange

#
# Initialize evdev and attempt to find Card Reader Device
#
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

#
# Record all keyboard events until KEY_KPENTER is pressed
#
def readData(reader):
    keyEvents = []
    reader.grab()
    for event in reader.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            temp = evdev.categorize(event)
            if temp.keystate:
                keyEvents.append(temp)
                if keyEvents[-1].keycode == "KEY_KPENTER":
                    break
    reader.ungrab()
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