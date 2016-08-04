import subprocess

def testRoot():
    p = subprocess.Popen('sudo -n echo', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #first = p.stdout.readlines()[0].decode("utf-8")
    retval = p.stdout.readlines()[0].find("sudo: a password is required") == -1
    wait = p.wait()
    return retval

if __name__ == '__main__':
    print(testRoot())