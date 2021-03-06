import os, time

class Handler:
    #expects secret, then url.
    datPath = "../dat/"
    def __init__(self, *args, **kwargs):
        #this defines object constant vars. I.E. API url, API access token etc. 
        self.objConst = ['url', 'secret']

        pos = len(args) + len(kwargs)
        if not pos == len(self.objConst):
            print("Not enough arguments, [HANDER INIT]")
            exit()
        try:
            for i, key in enumerate(self.objConst):
                value = kwargs.get(key, None) or args[ max(0, i - (pos -len(args)))]
                setattr(self, key, value)

        except IndexError:
            print("Malformed init args. [Handler]")
            exit()
    

        return

    def barfObj(self, pretty=True, secure = True):
        locVar = vars(self)
        if not pretty:
            print( locVar)
        else:
            for key in locVar:
                print("Key: ", key, "\tis:", locVar[key])

    #app specific. login, name, email fields should be populated
    def pullData(self):
        self.dat = ["HANDLER_DEFAULT"]
        return;

    def getData(self):
        return self.dat

    def __dumpData(self, f, dump= self.dat):
        with open(f, 'w') as memo:
            json.dump(dump, memo, indent=2)

    def prettyPrintData(self):
        print("SUPERCLASS METHOD")
        return

    def isRecent(self, filename, change=3600):
        if os.path.isfile(filename):
            if( time.time() - os.path.getmtime(filename)) < change:
                return True
        return False


