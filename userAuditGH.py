import os
import json
import requests
import boto3
import time
import csv

#global github connection info
github_tok = os.getenv("GITHUB_TOK")
githubURL = "https://api.github.com"
githubHeader = {'Accept': 'application/vnd.github.v3+json',\
            "Authorization":"token "+github_tok  }

datPath = "../dat/"

#########################################
#   Pull user info from Org page Github #
#########################################
def orgUserQuery():
    s = requests.Session()
    s.headers.update(githubHeader)
    payload = { "per_page":"100","page":1}
    orgMember = "/orgs/Infoblox-CTO/members?"
    jsonResp = []
    #use list to store response to gather muliitple queries for user count > 100
    while True:
        print("Call")
        resp = s.get( githubURL+orgMember, params=payload )
        payload['page'] += 1
        dat = json.loads(resp.text)
        if not dat:
            break;
        jsonResp += dat
    return jsonResp

#move to sperate file
def isRecent(filename, change=3600):
    if os.path.isfile(filename):
        if( time.time() - os.path.getmtime(filename)) < change:
            return True
    return False


#########################################
#   Query for rate limit.               #
#########################################

def rateQuery():
    resp = requests.get(githubURL+"/rate_limit")
    var = json.loads(resp.text)['resources']['core']
    var['reset'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(var['reset']))
    return var


#########################################
#   Pull data or get recent, return it  #
#########################################
def getGHDat():
    gh = datPath + "githubUsers.txt"

#UPDATE THIS SO IT UPDATES, NOT DELETES OLD DATA
#ON NEW QUERY, DELETE IF DOES NOT EXIST
    try:
        with open(gh, 'r') as memo:
            old = json.load(memo)
    except (FileNotFoundError, ValueError):
        old = []

    if not isRecent(gh, 86400):
        dat = orgUserQuery()
        #don't mess with this code it's leperous.
        for i in range(len(dat)):
            for oL in old:
                if oL['login'] == dat[i]['login']:
                    dat[i] = oL
    else:
        dat = old
    return dat


#########################################
#   Write Github Data after user Pulls  #
#########################################

def putGHDat(dat):
    gh = datPath + "githubUsers.txt" #hard coding this is bad an needs to be changed
    dat.sort(key=lambda x: x['login'])
    with open(gh, 'w') as memo:
        json.dump(dat, memo, indent=2)          


#########################################
#   Get emails form loggly HTML file    #
#   Assumes File Downloaded already     #
#########################################
def scrapeLoggly(filename):
    getStr = "infoblox.com"
    with open(filename) as f:
        proc =[elem for y in[x.strip().rstrip('\n').rsplit(' ') for x in f.readlines()] for elem in y if "infoblox.com" in elem]
    return proc[1:-1] #filter( ) Todo: implement actual regex 


#########################################
#   Read CSV, assumes downloaded        #
#########################################
def readCSV(fname):
    tmpLst = []
    with open(fname, 'r') as csvfile:
        read = csv.reader(csvfile)
        for row in read:
            tmpLst.append(row[0:4])
    return tmpLst
    
#########################################
#   Get user data (name) and            #
#   return with Access time appended    #
#########################################
#User data is equivalent to that of 
#the organization user query, except
#it contains more fields. 

def getUser(apiURL):

    print(apiURL)
    r = requests.get(apiURL, headers=githubHeader)
    user = json.loads(r.text)
    user['accessed'] = int(time.time())
    print(user, "\n")
    return user;


#########################################
#   Read CSV, assumes downloaded        #
#########################################

def pollGHUsers():
    users = getGHDat()
    users.sort(key=lambda x: x.get("accessed", 0))
    rt = rateQuery()
    print(rt)

    #prmagma
    for i in range(len(users)):
        if abs(time.time() - users[i].get('accessed',0)) > 7200:
            users[i] = getUser(users[i]['url'])
    putGHDat(users)

    return users


if __name__ == "__main__":
    GH = pollGHUsers()
    ldap = readCSV(datPath + "infoblox_employees.csv")
    boo = 0

    und = []
    for git in GH:
        git['name'] = (git['name'] or '').lower()
        for real in ldap:
            if (real[2].lower() in git['name'] and real[1].lower() in git['name'])\
                    or real[0] in git['login']: 
                boo = 1 #mark found in loop
                break

        if boo == 0:#it was not found in loop
            und.append(git)
        else:
            boo = 0

    [ print("Name:", x['name'],"Login:",  x['login']) for x in und]

    with open("bad_users.txt", 'w') as memo:
        json.dump(und, memo, indent=2)

    print("Length: ", len(und))
#print(data)

#print(scrapeLoggly("../Documents/scrape_loggly8.10.17.htm"))







