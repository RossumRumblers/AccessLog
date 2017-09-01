'''
A file of small misc. functions
'''

import socket
import subprocess
import httplib2

class Singleton(type):
    '''
    Singlton Design Pattern metaclass
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def testRoot():
    '''
    Test Root Access
    '''

    #run a simple command as root and check if we need a password
    p = subprocess.Popen(
        'sudo -n echo',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)

    retval = (p.stdout.readlines()[0].find("sudo: a password is required") == -1)
    p.wait()
    return retval

def testInternet():
    '''
    Check Internet Connection
    '''

    # attempt a connection to google and report success or not
    conn = httplib2.HTTPConnectionWithTimeout("www.google.com", timeout=None)

    try:
        conn.request("HEAD", "/")
        return True
    except socket.gaierror:
        return False
