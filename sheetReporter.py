#
# A file to simplify the upload and logging script
#

import os
from dependencies.GAPIFunc import *
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
_SECRET_FileName = "client_secret-RR.json"
_CRED_FileName   = "cred_store-RR.json"
_LOGIN_FileName  = "ActiveUsers"
_baseFolder = ".aLog"
_credFolder = "cred"


def _fileSetup():
	#API Secretsand access-cred file is in ~/.aLog/cred
	#Logged in User file is in ~/.aLog/ActiveUsers
	folderPath = os.path.join(os.path.expanduser('~'), _baseFolder)
    credfolder = os.path.join(folderPath, _credFolder)
	os.makedirs(folderPath, exist_ok=True)
    os.makedirs(credfolder, exist_ok=True)
	_SECRET_File = os.path.join(credfolder, _SECRET_FileName)
	_CRED_File = os.path.join(credfolder, _CRED_FileName)


	return [_SECRET_File, _CRED_File, ]

#
# Column Declarations
#
_IDColumnLetter = 'D' #Column of ID numbers
_IDColumnOffset = 3 #First row we can start searching for a user
_IDColumn = "{0}{1}:{0}".format(_IDColumnLetter,str(_IDColumnOffset))

_RrelevantInfo = ['B', 'I'] # Registered user relevant data columns
_URelevantInfo = ['A', 'D', 'G'] # Unregister user relevant data columns

#
# Miscellaneous Declarations
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
		credFiles = _fileSetup()
		print(credFiles[0])
		print(credFiles[1])
		self._service = createAPIService(getCredentials(credFiles[1], credFiles[0],
									_scopes, _applicationName, False), _discoveryUrl)

	def log(self, IDnum):
		try:
            # Get the number of entries in the Access Log
			searchList = requestRange(self._service, PasteSpreadsheet, "A2:A")
            # keep track of next available cell
			self.nextCell = len(searchList) + 2
            # get the last day of sign-in
			lastDate = datetime.strptime(searchList[-1][0], _dateFormat)
			if datetime.today().day != lastDate.day:
                # if the last day was yesterday, add an empty row
				self.nextCell +=1
		except(NoValueReturnedError):
			self.nextCell = 2

        #get a list of all registered users ID numbers
		IDlist = requestRange(self._service, CopySpreadsheet, _IDColumn)
		clockedtime = strftime(_dateFormat)
		userRow = None
        # search through ID list for the provided ID number
		for cell in range(0, len(IDlist)):
			if not IDlist[cell]:
				continue
			if IDlist[cell][0] == IDnum:
				userRow = cell+_IDColumnOffset
				break
		if not userRow:
            # Log an unregistered User
			updateRange(self._service, PasteSpreadsheet, "{0}{1}:{0}{1}".format(_URelevantInfo[0],
						self.nextCell), [[clockedtime]])
			updateRange(self._service, PasteSpreadsheet, "{0}{1}:{0}{1}".format(_URelevantInfo[1],
						self.nextCell), [[IDnum]])
			updateRange(self._service, PasteSpreadsheet, "{0}{1}:{0}{1}".format(_URelevantInfo[2],
                        self.nextCell), [["Unregistered"]])
			self.nextCell +=1
			return("Unregistered user {0} clocked in at {1}".format(IDnum, clockedtime))
		else:
            # Log a registered User

            #get the user's information from the members list
			result = requestRange(self._service, CopySpreadsheet,
                        "{0}{2}:{1}{2}".format(_RrelevantInfo[0], _RrelevantInfo[1], userRow))

			updateRange(self._service, PasteSpreadsheet, "B{0}:{0}".format(self.nextCell), result)
			updateRange(self._service, PasteSpreadsheet, "A{0}:A{0}".format(self.nextCell), [[clockedtime]])

			self.nextCell +=1
			return("User {0} {1} clocked in at {2}".format(result[0][0], result[0][1], clockedtime))

if __name__ == '__main__':
	_fileSetup()