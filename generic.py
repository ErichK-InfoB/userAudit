import os, time

def isRecent(filename, time=3600):
    if os.path.isfile(filename):
        if(time.time() - os.path.getmtime(filename)) < time:
            return True
    return False




