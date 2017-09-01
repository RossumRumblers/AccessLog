#
# A file to simplify the upload and logging script
#

import os

from datetime import datetime
from JSONReader import JSONReader

from dependencies import GAPIFunc
from dependencies.miscFunc import Singleton

#
# Google Spreadsheet Declarations
#
_scopes = 'https://www.googleapis.com/auth/spreadsheets' #Read/Write Spreadhseet Scope
_discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4') #API Discovery URL
_applicationName = "Kiosk Access"

#
# File name and Path Declarations
#
_SERVICE_FileName = "serviceCred.json"
_Folder = ".cred"

def _fileSetup():
    '''
    Build path to Service account JSON store

    API service Account file is in ~/.cred
    '''
    folderPath = os.path.join(os.path.expanduser('~'), _Folder)
    _SERVICE_File = os.path.join(folderPath, _SERVICE_FileName)
    #return _SERVICE_File
    return 'secrets/serviceCred.json'

#
# Column Declarations
#
_IDColumnOffset = 2

#ID Column
_IDColumn = "D{0}:D".format(_IDColumnOffset)

#registered user: columns to read user data from
# b = First Name
# c = Last Name
# d = Last Name
_relevantInfo = ['B', 'D']
_MembersSheetName = "Sheet1"

_timeColumn = 'A'

# Title information for Sheet
_FirstRowDim = "A1:D1"
_FirstRow = ["Date: Time",
             "First Name",
             "Last Name",
             "ASU ID #"]

#
# Miscellaneous Declarations
#
_dateFormat = "%Y-%m-%d %H:%M:%S"

class Reporter(metaclass=Singleton):
    '''
    Usage class for sheetreporter
    '''
    def __init__(self):
        serviceFile = _fileSetup()
        self._service = GAPIFunc.createAPIService(
            GAPIFunc.getServiceCredentials(serviceFile, _scopes))

        #to silence pylint:
        self._sheetName = None
        self.nextCell = None

    def log(self, IDnum, Club):
        '''
        Log the User's ID
        '''
        self._sheetName = "{0}-{1}".format(datetime.today().strftime('%B'), datetime.today().year)

        # get specific information related to club
        ClubShortName = JSONReader().getClubNameShort(Club)
        ClubRosterID = JSONReader().getRosterID(Club)
        ClubAccessID = JSONReader().getLogID(Club)
        ClubRosterSheet = JSONReader().getMemberSheet(Club)

        # get the next available cell for writing
        try:
            searchList = GAPIFunc.requestRange(self._service, ClubAccessID, self._sheetName, "A2:A")
            self.nextCell = len(searchList) + 2

            # if the last entry was on a different Day, skip a line
            lastDate = datetime.strptime(searchList[-1][0], _dateFormat)
            if datetime.today().day != lastDate.day:
                self.nextCell += 1

        except GAPIFunc.NoValueReturnedError:
            # No Data in sheet, start fresh
            GAPIFunc.updateRange(
                self._service,
                ClubAccessID,
                self._sheetName,
                _FirstRowDim,
                [_FirstRow])

            self.nextCell = 2
        except GAPIFunc.InvalidRangeError:
            #sheet doesn't exist, create it and populate it
            GAPIFunc.addSheet(self._service, ClubAccessID, self._sheetName)
            GAPIFunc.updateRange(
                self._service,
                ClubAccessID,
                self._sheetName,
                _FirstRowDim,
                [_FirstRow])
        finally:
            self.nextCell = 2

        # get Searchable List of User ID's
        IDlist = GAPIFunc.requestRange(self._service, ClubRosterID, ClubRosterSheet, _IDColumn)

        # get clocked time of the User
        clockedtime = datetime.now().strftime(_dateFormat)

        # Search IDlist for the user ID
        userRow = None
        for cell in range(0, len(IDlist)):
            # Null cell check to prevent crashing
            if not IDlist[cell]:
                continue
            #
            if IDlist[cell][0] == IDnum:
                userRow = cell + _IDColumnOffset
                break
        retval = None
        if userRow:
            #get user's info
            result = GAPIFunc.requestRange(
                self._service,
                ClubRosterID,
                ClubRosterSheet,
                "{0}{2}:{1}{2}".format(
                    _relevantInfo[0],
                    _relevantInfo[1],
                    userRow))

            # log user to spreadsheet
            GAPIFunc.updateRange(
                self._service,
                ClubAccessID,
                self._sheetName,
                "{0}{2}:{1}{2}".format(
                    _timeColumn,
                    _relevantInfo[1],
                    self.nextCell),
                [[clockedtime] + result[0]])

            retval = "{0} User {1} {2} clocked in at {3}".format(
                ClubShortName,
                result[0][0],
                result[0][1],
                clockedtime)
        else:
            # log unregistered user to spreadsheet
            GAPIFunc.updateRange(
                self._service,
                ClubAccessID,
                self._sheetName,
                "{0}{2}:{1}{2}".format(
                    _timeColumn,
                    _relevantInfo[1],
                    self.nextCell),
                [[clockedtime, 'Unregistered', '', IDnum]])

            self.nextCell += 1
            retval = "Unregistered user {0} clocked in at {1}".format(IDnum, clockedtime)

        return retval

#just in case
if __name__ == '__main__':
    _fileSetup()
