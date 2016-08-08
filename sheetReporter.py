#
# A file to simplify the upload and logging script
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
_scopes = 'https://www.googleapis.com/auth/spreadsheets' #Read/Write Spreadhseet Scope
_discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4') #API Discovery URL
_applicationName = "Lab Access Recorder Script" 

#
# File name and Path Declarations
#
_secret_FileName = "client_secret-RR.json"
_CRED_FileName = "cred-store-RR.json"
_CRED_FilePath = os.path.join(os.path.expanduser("~"), ".cred")
os.makedirs(_CRED_FilePath, exist_ok=True);
_CRED_File = os.path.join(_CRED_FilePath, _CRED_FileName)

#
# Column Declarations
#
_IDColumnLetter = 'D' #Column of ID numbers
_IDColumnOffset = 3 #First row we can start searching for a user.
_IDColumn = _IDColumnLetter + str(_IDColumnOffset) + ":" + _IDColumnLetter
_RrelevantInfo = ['B', 'I']
_URelevantInfo = ['A', 'D', 'G']

#
# Miscellaneous 
#
_dateFormat = "%Y-%m-%d %H:%M:%S"

# define singleton metclass
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#define usage class for sheetreporter
class Reporter(metaclass=Singleton):
    def __init__(self):
        self._service = createAPIService(getCredentials(_CRED_File, _secret_FileName, 
                                    _scopes, _applicationName, False), _discoveryUrl)

    ###TODO###
    # comments


    ###FEATURE###
    # Open google form for unregistered users
    #
    #  Josh mentions wanting unregistered users have a google form pop up to register
    #  Google does not allow custom redirects(to close the browser window afterwards)
    # 
    #1 check form for user completed(probably need to have either a timeout or check active processes or something...)
    #2 look for QT browser window to see if i have greater control over it.(doubtful)
    def log(self, IDnum):
        try:
            searchList = requestRange(self._service, PasteSpreadsheet, "A2:A")
            self.nextCell = len(searchList) + 2
            lastDate = datetime.strptime(searchList[-1][0], _dateFormat)
            if datetime.today().day != lastDate.day:
                self.nextCell +=1
        except(NoValueReturnedError):
            self.nextCell = 2

        IDlist = requestRange(self._service, CopySpreadsheet, _IDColumn)
        clockedtime = strftime(_dateFormat) 
        userRow = None
        for cell in range(len(IDlist)):
            if IDlist[cell][0] == IDnum:
                userRow = cell+_IDColumnOffset
                break;
        if not userRow:
            updateRange(self._service, PasteSpreadsheet, 
                        "{0}{1}:{0}{1}".format(_URelevantInfo[0],self.nextCell), [[clockedtime]])
            updateRange(self._service, PasteSpreadsheet,
                        "{0}{1}:{0}{1}".format(_URelevantInfo[1],self.nextCell), [[IDnum]])
            updateRange(self._service, PasteSpreadsheet, 
                        "{0}{1}:{0}{1}".format(_URelevantInfo[2],self.nextCell), [["Unregistered"]])
            self.nextCell +=1
            return("Unregistered user {0} clocked in at {1}".format(IDnum, clockedtime))
        else:        
            rangeRequest = "{0}{2}:{1}{2}".format(_RrelevantInfo[0], _RrelevantInfo[1], userRow)
            result = requestRange(self._service, CopySpreadsheet, rangeRequest)
            rangeUpdate = "B{0}:{0}".format(self.nextCell)
            updateRange(self._service, PasteSpreadsheet, rangeUpdate, result)
            rangeUpdate = "A{0}:A{0}".format(self.nextCell)
            updateRange(self._service, PasteSpreadsheet, rangeUpdate, [[clockedtime]])
            self.nextCell +=1
            return("User {0} {1} clocked in at {2}".format(result[0][0], result[0][1], clockedtime))

if __name__ == '__main__':
    pass