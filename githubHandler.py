from handler import *
import requests
import json

#This file is intended to hold multiple classes for each 
#aspect of the github API. it uses "handler" as a base class.
#a refactor could incorporate a generic github handler parent class

#this refactor could also consider a class to hold all different classes
#and allow calls to be aliased inside of this single class

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
        self.dat = []
        for u in self.orgUserQuery():
            print(u['url'])
            self.dat.append(json.loads(\
                    requests.get(u['url'], headers=self.header).text))
        if self.rl:
            self.__dumpData(orgFile, self.dat)

    def __dumpData(self, f, dump):
        with open(f, 'w') as memo:
            json.dump(dump, memo, indent=2)



if __name__ == "__main__":
    secret = os.getenv("GITHUB_TOK")

    #test githubUser OBJ
    h = GitHubUserHandler(secret)
    h.pullData()
    print(*h.getData(), sep='\n')
    h.barfObj()
    print("Is recent?", h.isRecent("./handler.py"))

