#
# A file to simplify the upload and logging script
#

import os
import re
from time import strftime
from datetime import datetime
from dependencies import GAPIFunc
from JSONReader import JSONReader
from dependencies.miscFunc import *

#
# Google Spreadsheet Declarations
#
_scopes = 'https://www.googleapis.com/auth/spreadsheets' #Read/Write Spreadhseet Scope
_discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4') #API Discovery URL
_applicationName = "Kiosk Access"

#
# File name and Path Declarations
#
_SECRET_FileName = "client_secret-S90.json"
_CRED_FileName = "cred_store-S90.json"
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
_IDColumnOffset = 3
_IDColumn = "D{0}:D".format(_IDColumnOffset) # mandatory
_RrelevantInfo = ['B', 'I']                  # mandatory
_URelevantInfo = ['A', 'D', 'G']             # mandatory
_MembersSheetName = "Sheet1"

_FirstRowDim = "A1:I1"
_FirstRow = ["Date: Time",
			 "First Name",
			 "Last Name",
			 "ASU ID #",
			 "ASU Email Address",
			 "Major",
			 "Membership Status",
			 "Undergraduate/Graduate Student",
			 "Alternate Email"]

#
# Miscellaneous Declarations
#
_dateFormat = "%Y-%m-%d %H:%M:%S"
_sheetNameRE = '([^-]{3,9})-(\d{4})' # Month-Year


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
		self._service = GAPIFunc.createAPIService(GAPIFunc.getCredentials(credFiles[1], credFiles[0],
									_scopes, _applicationName, False), _discoveryUrl)

	def log(self, IDnum, Club):
		self._month = datetime.today().month
		self._sheetName = "{0}-{1}".format(getMonthName(self._month), datetime.today().year)

		# get specific information related to club
		ClubShortName = JSONReader().getClubNameShort(Club)
		ClubRosterID = JSONReader().getRosterID(Club)
		ClubAccessID = JSONReader().getLogID(Club)
		ClubRosterSheet = JSONReader().getMemberSheet(Club)
		
		# get the next available cell for writing
		try:
			searchList = GAPIFunc.requestRange(self._service, ClubAccessID, self._sheetName, "A2:A")
			self.nextCell = len(searchList) + 2
			lastDate = datetime.strptime(searchList[-1][0], _dateFormat)
			# if the last entry was on a different Day, skip a line
			if datetime.today().day != lastDate.day:
				self.nextCell += 1
			
		except GAPIFunc.NoValueReturnedError:
			# No Data in spreadhseet, start fresh
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, _FirstRowDim, [_FirstRow])
			self.nextCell = 2
		except GAPIFunc.InvalidRangeError:
			GAPIFunc.addSheet(self._service, ClubAccessID, self._sheetName)
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, _FirstRowDim, [_FirstRow])
			self.nextCell = 2

		# get Searchable List of User ID's
		IDlist = GAPIFunc.requestRange(self._service, ClubRosterID, ClubRosterSheet, _IDColumn)
		print(IDlist)

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
		
		if userRow:
			#get user's info
			result = GAPIFunc.requestRange(self._service, ClubRosterID, ClubRosterSheet, "{0}{2}:{1}{2}".format(_RrelevantInfo[0], _RrelevantInfo[1], userRow))

			# log user to spreadsheet
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, "B{0}:{0}".format(self.nextCell), result)
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, "A{0}:A{0}".format(self.nextCell), [[clockedtime]])
			self.nextCell +=1
			return("{0} User {1} {2} clocked in at {3}".format(ClubShortName, result[0][0], result[0][1], clockedtime))
			
		else:
			# log unregistered user to spreadsheet
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, "{0}{1}:{0}{1}".format(_URelevantInfo[0],self.nextCell), [[clockedtime]])
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, "{0}{1}:{0}{1}".format(_URelevantInfo[1],self.nextCell), [[IDnum]])
			GAPIFunc.updateRange(self._service, ClubAccessID, self._sheetName, "{0}{1}:{0}{1}".format(_URelevantInfo[2],self.nextCell), [["Unregistered"]])
			self.nextCell +=1
			return("Unregistered user {0} clocked in at {1}".format(IDnum, clockedtime))

if __name__ == '__main__':
	_fileSetup()