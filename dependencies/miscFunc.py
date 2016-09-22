#
# A file of small misc. functions
#

import os
import httplib2
import subprocess

#
# Test Root Access
#
def testRoot():
	p = subprocess.Popen('sudo -n echo', shell=True, stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT, universal_newlines=True)
	retval = (p.stdout.readlines()[0].find("sudo: a password is required") == -1)
	wait = p.wait()
	return retval

#
# Check Internet Connection
#
def testInternet():
	conn = httplib2.HTTPConnectionWithTimeout("www.google.com",timeout=None)
	try:
		conn.request("HEAD", "/")
		return True
	except:
		return False

def getMonthName(num):
	try:
		return ['January',
			'February',
			'March',
			'April',
			'May',
			'June',
			'July',
			'August',
			'September',
			'October',
			'November',
			'December'][num - 1]
	except(IndexError):
		return None