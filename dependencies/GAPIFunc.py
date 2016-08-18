#
# Functions For simplyifying access to the Google API
#

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

class InvalidInputTypeError(Exception): #consider removal
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
# Functions
#


#
# Retrieve Access Ceredentials
#
def getCredentials(CRED_File, Secret_File, Scopes, APPLICATION_NAME, rebuild):
    # Attempt to retreieve credentials from file
    store = oauth2client.file.Storage(CRED_File)
    credentials = store.get()
    if not credentials or credentials.invalid or rebuild:
        # Get Credentials from server using Client keys
        flow = client.flow_from_clientsecrets(Secret_File, Scopes)
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
        return None
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    if not service:
        return None
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

def updateRange(service, SpreadsheetId, range, sheetData):
    requestBody = {'values': sheetData}
    returnedRange = service.spreadsheets().values().update(spreadsheetId=SpreadsheetId, range=range, body=requestBody, valueInputOption="USER_ENTERED").execute()
    if not returnedRange:
        raise RangeNotUpdatedError(valueRange)
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

def autoResizeRange(service, SpreadsheetId, range):
    """function currently broken
    """ 
    requestBody = {
        'requests': [{
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": SpreadsheetId,
                        "dimension": "Columns",
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