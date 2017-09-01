#
# Functions For simplyifying access to the Google API
#
###TODO###
# Notate Parameters
# Expand Commands
# Make this a class so I don't need to pass service into every function

import httplib2shim
import oauth2client
import googleapiclient

from oauth2client import tools
from oauth2client import client
from oauth2client import service_account
from apiclient import discovery

#
# Exception Classes
#
class NoValueReturnedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidRangeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RangeNotUpdatedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def getOath2Credentials(CRED_File, SECRET_File, Scopes, APPLICATION_NAME, rebuild):
    '''
    Retrieve Access Credentials from Oauth2 client secrets
    '''

    # Attempt to retreieve cached credentials from file
    store = oauth2client.file.Storage(CRED_File)
    credentials = store.get()
    if not credentials or credentials.invalid or rebuild:
        # Get Credentials from server using Client Secrets
        flow = client.flow_from_clientsecrets(SECRET_File, Scopes)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
    return credentials

def getServiceCredentials(SERVICE_File, Scopes):
    '''
    Retrieve Access Credentials for Service Account
    '''

    # build credentials object from JSON file
    return service_account.ServiceAccountCredentials.from_json_keyfile_name(SERVICE_File, Scopes)

def createAPIService(credentials, discoveryUrl=None):
    '''
    Create API Service for acccessing spreadsheets
    '''
    http = credentials.authorize(httplib2shim.Http())
    if not http:
        return None

    if discoveryUrl:
        # distinguishes between Service and Client Secret service Creation
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    else:
        service = discovery.build('sheets', 'v4', http=http)
    if not service:
        return None
    return service

def requestRange(service, SpreadsheetId, SheetName, req_range):
    '''
    Request Range via get command
    '''

    a1Not = "{0}!{1}".format(SheetName, req_range)

    try:
        spreadServ = service.spreadsheets().values()
        retRange = spreadServ.get(spreadsheetId=SpreadsheetId, range=a1Not).execute()
        values = retRange.get('values', [])
        if not values:
            raise NoValueReturnedError(a1Not)
        else:
            return values
    except googleapiclient.errors.HttpError as e:
        raise InvalidRangeError(a1Not)

def requestRanges(service, SpreadsheetId, SheetName, ranges):
    '''
    Request Ranges via batchGet command
    '''
    result = []
    a1Notes = []
    for req_range in ranges:
        a1Notes.append(SheetName + "!" + req_range)
    try:
        spreadServ = service.spreadsheets().values()
        returnedRanges = spreadServ.batchGet(spreadsheetId=SpreadsheetId, ranges=a1Notes).execute()
        values = returnedRanges.get('valueRanges', [])
        if not values:
            raise NoValueReturnedError(a1Notes)
        else:
            for elem in values:
                result.append(elem.get('values', []))
            return result
    except googleapiclient.errors.HttpError as e:
        raise InvalidRangeError(a1Notes)

def updateRange(service, SpreadsheetId, SheetName, req_range, sheetData):
    '''
    Update
    '''
    requestBody = {'values': sheetData}
    a1Note = (SheetName + "!" + req_range)

    spreadServ = service.spreadsheets().values()
    returnedRange = spreadServ.update(
        spreadsheetId=SpreadsheetId,
        range=a1Note,
        body=requestBody,
        valueInputOption="USER_ENTERED").execute()

    if not returnedRange:
        raise RangeNotUpdatedError(returnedRange)
    return returnedRange

def getAllSheets(service, SpreadsheetId):
    '''
    Get a list of all sheets on the spreadsheet
    '''
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SpreadsheetId).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheetsArr = []
    for sheet in sheets:
        prop = sheet.get('properties', {})
        item = {
            'SheetId': prop.get('SheetId', ""),
            'title':   prop.get('title', ""),
            'index':   prop.get('index', "")
        }
        sheetsArr.append(item)
    return sheetsArr

def batchUpdate(service, SpreadsheetId, requests):
    '''
    Execute request(s) using JSON

    not..really for public use?

    idk be careful
    '''
    body = {
        'requests': requests
    }
    service.spreadsheets().batchUpdate(spreadsheetId=SpreadsheetId, body=body).execute()

def autoResizeDimensions(service, SpreadsheetId, indexRange):
    '''
    Auto resize the dimensions of the requested range
    '''
    request = []
    request.append({
        'autoResizeDimensions': {
            'dimensions': {
                'sheetId': 0,
                'dimension': 'Columns',
                'startIndex': indexRange[0],
                'endIndex': indexRange[1],
            }
        }
    })
    batchUpdate(service, SpreadsheetId, request)

def addSheet(service, SpreadsheetId, sheetName):
    '''
    append a new sheet to an existing spreadsheet
    '''
    index = int(getAllSheets(service, SpreadsheetId)[-1].get('index', 0))
    request = []
    request.append({
        'addSheet': {
            'properties': {
                "sheetId": index + 1,
                "title": sheetName,
                "index": index + 1,
                "sheetType": 'GRID',
                "gridProperties": {
                    "rowCount": 1000,
                    "columnCount": 26,
                    "frozenRowCount": 0,
                    "frozenColumnCount": 0,
                    "hideGridlines": False,
                },
                "hidden": False,
                "tabColor": {
                    "red":   1.0,
                    "green": 1.0,
                    "blue":  1.0,
                    "alpha": 1.0,
                },
                "rightToLeft": False,
            }
        }
    })
    batchUpdate(service, SpreadsheetId, request)
