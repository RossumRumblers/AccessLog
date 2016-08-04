#!/bin/python3

#
#version 1.0
#
import os
from dependencies import *
from time import strftime
from datetime import datetime

#
# Google Spreadsheet Declarations
#
CopySpreadsheet = '1E_3Ulg6gMEhFclcggq0bOumZyezTo5WpshTpfFpXaLI'
PasteSpreadsheet = '1Fu1LYy0Jp560BZeSySq5s-cvsdjj-RJ3Nde4V8siWB8'
Scopes = 'https://www.googleapis.com/auth/spreadsheets' #Read/Write Spreadhseet Scope
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4') #API Discovery URL
applicationName = "LabAccessRecorderScript" 

#
# File name and Path Declarations
#
Secret_FileName = "client_secret-RR.json"
CRED_FileName = "cred-store-RR.json"
CRED_FilePath = os.path.join(os.path.expanduser("~"), ".cred")
os.makedirs(CRED_FilePath, exist_ok=True);
CRED_File = os.path.join(CRED_FilePath, CRED_FileName)

#
# Column Declarations
#
IDColumnLetter = 'D' #Column of ID numbers
IDColumnOffset = 3 #First row we can start searching for a user.
RrelevantInfo = ['B', 'I']
URelevantInfo = ['A', 'D', 'G']

#
# Miscellaneous 
#
IDregex = ";601744(\d{10})1(\d{10})\?"
device_IDs = ["5131","2007"]
dateFormat = "%Y-%m-%d %H:%M:%S"

#
# Main
#
### TODO ###
# redo comments to make sense
# check in/Check out
# create a new sheet for each month
# #IP# look into a fancy GUI
if __name__ == '__main__':
# # #Create API Service and Access

    service = createAPIService(getCredentials(CRED_File, Secret_FileName, Scopes, applicationName, False), discoveryUrl)
    readerDevice = initReader(device_IDs[0], device_IDs[1])

    searchList = requestRange(service, PasteSpreadsheet, "A1:A")
    print(searchList)
    nextCell = len(searchList) + 1

    lastDate = datetime.strptime(searchList[-1][0], dateFormat)
    lastDate.day
    if datetime.today().day != lastDate.day:
        nextCell +=1

# # #Finding and Copying Appropriate User

    IDColumn = IDColumnLetter + str(IDColumnOffset) + ":" + IDColumnLetter #Build ID number column
    IDlist = requestRange(service, CopySpreadsheet, IDColumn)
    while(True):
        print("Please swipe your ASU ID Card.")
        while(True):
            IDnum = extractID(interpretEvents(readData(readerDevice)), IDregex)
            if not IDnum:
                print("Please scan an ASU ID Card.")
                continue
            else:
                break
        clockedtime = strftime(dateFormat)        
        for cell in range(len(IDlist)):
            if IDlist[cell][0] == IDnum:
                userRow = cell+IDColumnOffset
                break;
        if not userRow:
            print("User is not a member. Logging...")
            updateRange(service, PasteSpreadsheet, 
                        "{0}{1}:{0}{1}".format(URelevantInfo[0],nextCell), [[clockedtime]], "RAW")
            updateRange(service, PasteSpreadsheet,
                        "{0}{1}:{0}{1}".format(URelevantInfo[0],nextCell), [[IDnum]], "USER_ENTERED")
            updateRange(service, PasteSpreadsheet, 
                        "{0}{1}:{0}{1}".format(URelevantInfo[0],nextCell), [["Unregistered"]], "USER_ENTERED")
        else:        
            rangeRequest = "{0}{2}:{1}{2}".format(RrelevantInfo[0], RrelevantInfo[1], userRow)
            result = requestRange(service, CopySpreadsheet, rangeRequest)
            print(result)
            print("User {0} {1} clocked in at {2}".format(result[0][0], result[0][1], clockedtime))
            rangeUpdate = "B{0}:{0}".format(nextCell)
            updateRange(service, PasteSpreadsheet, rangeUpdate, result, "USER_ENTERED")
            rangeUpdate = "A{0}:A{0}".format(nextCell)
            updateRange(service, PasteSpreadsheet, rangeUpdate, [[clockedtime]], "RAW")
        nextCell +=1
    