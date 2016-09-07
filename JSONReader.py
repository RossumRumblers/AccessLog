import json

#
# File Declarations
#
JSONFile = "ClubList.json"

class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class JSONReader(metaclass=Singleton) : 
	JSONdata = None

	def __init__(self):
		with open(JSONFile) as f:
			self.JSONdata=json.loads("".join(l.rstrip() for l in f))
	
	def getClubList(self):
		return self.JSONdata['Clubs']
	
	def getClubNameShort(self,clubName):
		return self.JSONdata['Club-info'][clubName]['Short Name']

	def getClubNameLong(self,clubName):
		return self.JSONdata['Club-info'][clubName]['Long Name']
	
	def getRosterID(self,clubName):
		return self.JSONdata['Club-info'][clubName]['Member List']

	def getLogID(self,clubName):
		return self.JSONdata['Club-info'][clubName]['Log File']

if __name__ == '__main__':
	club = JSONReader().getClubList()[0]
	print(JSONReader().getClubNameShort(club))
	print(JSONReader().getClubNameLong(club))
	print(JSONReader().getRosterID(club))
	print(JSONReader().getLogID(club))