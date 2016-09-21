#
# Functions For simplyifying access to the Google API
#

import httplib2shim
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
	http = credentials.authorize(httplib2shim.Http())
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

def getAllSheets(service, SpreadsheetId):
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
	body = {
		'requests': requests
	}
	service.spreadsheets().batchUpdate(spreadsheetId=SpreadsheetId, body=body).execute()

def autoResizeDimensions(service, SpreadsheetId, indexRange):
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
	index = int(getSheets(service,SpreadsheetId)[-1].get('index', 0))
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