from handler import *
import requests
import json
from multiprocessing import Pool

#This file is intended to hold multiple classes for each 
#aspect of the github API. it uses "handler" as a base class.
#a refactor could incorporate a generic github handler parent class

#this refactor could also consider a class to hold all different classes
#and allow calls to be aliased inside of this single class



#this must be at top level of module because python is weird
#this is a func used to multithread queries so that it is much faster
def tProc(head, chunk):
    tmp = []
    for i in chunk:
        print(i['url'])
        tmp.append(json.loads(\
                requests.get(i['url'], headers=head).text))
    return tmp



class GitHubUserHandler(Handler):
    def __init__(self, secret, rateLim = True):
        self.rl = rateLim
        #default init
        Handler.__init__(self, "https://api.github.com", secret)
        
        self.orgMemberExt = "/orgs/Infoblox-CTO/members?"
        self.header = {'Accept': "application/vnd.github.v3+json",\
                                "Authorization": "token "+self.secret }
        

    def rateQuery(self):
        r = requests.get(self.url+"/rate_limit", headers=self.header)
        return r.text

    def orgUserQuery(self):
        s = requests.Session()
        s.headers.update(self.header)
        payload ={"per_page": 100, "page":1}
        jsonResp=[]
        while True:
            resp = s.get(self.url+self.orgMemberExt, params=payload)
            retDat = json.loads(resp.text)
            if not retDat:
                break;
            jsonResp += retDat
            payload['page'] +=1
        return jsonResp

#in this use case this code will grab Infoblox org data from github
#get user data, load text as json, append user to "users"
#if debug print apiURL
    def pullData(self):
        orgFile = Handler.datPath + "GHOrgMem.txt"
        if self.rl and self.isRecent(orgFile):
            self.dat = json.load(open(orgFile, 'r'))
            return

        self.dat = []
        print("Grabbing user data, this may take a moment")
        orgUsr = self.orgUserQuery()
        cSize = 10
        tmpIn = [(self.header, orgUsr[i:i+cSize]) for i in range(0, len(orgUsr), cSize)]
        with Pool(len(tmpIn)) as p:
            users = p.starmap(tProc, tmpIn)
            
        if self.rl:
            self.__dumpData(orgFile)


    

    def __dumpData(self, f):
        with open(f, 'w') as memo:
            json.dump(self.dat, memo, indent=2)



if __name__ == "__main__":
    secret = os.getenv("GITHUB_TOK")

    #test githubUser OBJ
    h = GitHubUserHandler(secret)
    h.pullData()
   # print(*h.getData(), sep='\n')
    h.barfObj()
    print("Is recent?", h.isRecent("./handler.py"))

