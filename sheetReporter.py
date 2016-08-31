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
_CRED_FileName = "cred_store-RR.json"
_Folder = ".cred"

def _fileSetup():
	#API Secrets file is in ~/.cred/secrets
	#API access file is in ~/.cred
	folderPath = os.path.join(os.path.expanduser('~'), _Folder)
	os.makedirs(folderPath, exist_ok=True)
	_SECRET_File = os.path.join(folderPath, _SECRET_FileName)
	_CRED_File = os.path.join(folderPath, _CRED_FileName)
	return [_SECRET_File, _CRED_File]

#
# Column Declarations
#
_IDColumnLetter = 'D' #Column of ID numbers
_IDColumnOffset = 3 #First row we can start searching for a user.
_IDColumn = _IDColumnLetter + str(_IDColumnOffset) + ":" + _IDColumnLetter
_RrelevantInfo = ['B', 'I']
_URelevantInfo = ['A', 'D', 'G']

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

	###TODO###
	# comments
	def log(self, IDnum):
		print("IDnum")
		print("doing nextCell")
		try:
			print("0")
			searchList = requestRange(self._service, PasteSpreadsheet, "A2:A")
			print(searchList)
			print("1")
			self.nextCell = len(searchList) + 2
			print("2")
			lastDate = datetime.strptime(searchList[-1][0], _dateFormat)
			print("3")
			if datetime.today().day != lastDate.day:
				self.nextCell +=1
			print("4")
		except(NoValueReturnedError):
			print("5")
			self.nextCell = 2
		print("6")
		print("getting IDlist")
		IDlist = requestRange(self._service, CopySpreadsheet, _IDColumn)
		print("getting clocked date")
		clockedtime = datetime.now().strftime(_dateFormat)
		userRow = None
		print("checking IDlist")
		for cell in range(0, len(IDlist)):
			if not IDlist[cell]:
				continue
			if IDlist[cell][0] == IDnum:
				userRow = cell+_IDColumnOffset
				break
		print("checking user")
		if not userRow:
			print("unregistered user")
			updateRange(self._service, PasteSpreadsheet,
						"{0}{1}:{0}{1}".format(_URelevantInfo[0],self.nextCell), [[clockedtime]])
			updateRange(self._service, PasteSpreadsheet,
						"{0}{1}:{0}{1}".format(_URelevantInfo[1],self.nextCell), [[IDnum]])
			updateRange(self._service, PasteSpreadsheet,
						"{0}{1}:{0}{1}".format(_URelevantInfo[2],self.nextCell), [["Unregistered"]])
			self.nextCell +=1
			print("finishing unregistered user")
			return("Unregistered user {0} clocked in at {1}".format(IDnum, clockedtime))
		else:
			print("registered user")
			rangeRequest = "{0}{2}:{1}{2}".format(_RrelevantInfo[0], _RrelevantInfo[1], userRow)
			result = requestRange(self._service, CopySpreadsheet, rangeRequest)
			rangeUpdate = "B{0}:{0}".format(self.nextCell)
			updateRange(self._service, PasteSpreadsheet, rangeUpdate, result)
			rangeUpdate = "A{0}:A{0}".format(self.nextCell)
			updateRange(self._service, PasteSpreadsheet, rangeUpdate, [[clockedtime]])
			self.nextCell +=1
			print("finishing registered user")
			return("User {0} {1} clocked in at {2}".format(result[0][0], result[0][1], clockedtime))

if __name__ == '__main__':
	_fileSetup()
