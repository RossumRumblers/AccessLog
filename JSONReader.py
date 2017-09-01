'''
Class for interpretting the JSON Club List
'''

import os
import json

from dependencies.miscFunc import Singleton

#
# File Declarations
#
JSONFile = "ClubList.json"

class JSONReader(metaclass=Singleton):
    JSONdata = None

    def __init__(self):
        #open file with requirement to close
        JSONFilePath = os.path.join(os.path.dirname(__file__), JSONFile)
        with open(JSONFilePath) as f:
            #open JSON file as a string and strip line endings
            self.JSONdata = json.loads("".join(l.rstrip() for l in f))

    #get list of active clubs
    def getClubList(self):
        return self.JSONdata['Clubs']

    #get specfic Club data
    def getClubNameShort(self, clubID):
        return self.JSONdata['Club-info'][clubID]['Short Name']

    def getClubNameLong(self, clubID):
        return self.JSONdata['Club-info'][clubID]['Long Name']

    def getRosterID(self, clubID):
        return self.JSONdata['Club-info'][clubID]['Member List']

    def getMemberSheet(self, clubID):
        return self.JSONdata['Club-info'][clubID]['Member Sheet']

    def getLogID(self, clubID):
        return self.JSONdata['Club-info'][clubID]['Log File']

    def getClubAllowed(self, clubID):
        return self.JSONdata['Club-info'][clubID]['Allow']


if __name__ == '__main__':
    #test Functions
    club = JSONReader().getClubList()[0]
    print(JSONReader().getClubNameShort(club))
    print(JSONReader().getClubNameLong(club))
    print(JSONReader().getRosterID(club))
    print(JSONReader().getMemberSheet(club))
    print(JSONReader().getLogID(club))
    print(JSONReader().getClubAllowed(club))
