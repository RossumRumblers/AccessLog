import json
import httplib2shim

from dependencies import GAPIFunc

from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery

#test parameters
spreadsheetId = '1OI8mkH1t9MHRp8kVPmpuop0C6chsS0xKyyVSg1gXU9w'
sheetName = 'Form Responses 1'
a1_notation_request = 'A1'

scopes = ['https://www.googleapis.com/auth/spreadsheets']
service = GAPIFunc.createAPIService(
            GAPIFunc.getServiceCredentials('serviceCred.json', scopes))

returnedRange = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range="{0}!{1}".format(sheetName, a1_notation_request)).execute()
values = returnedRange.get('values', [])

print(values)
