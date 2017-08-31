import githubHandler
import sys, os



def githubUserReport():
    secret = os.getenv("GITHUB_TOK")
    userObj = githubHandler.GitHubUserHandler(secret)
    userObj.pullData()
    


def logglyUserReport():
    return

def sysdigUserReport():
    return

def main():
    
    

    #Users
    #LDAP?

        #Loggly

        #Sysdig

        #Gibhub

if __name__ == "__main__":
    main()
