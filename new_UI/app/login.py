##########################################################################
# FileName - login.py
# Login page for authentication
# NOTE - you cannot add much to spice up the GUI unless it exists
#        in this file (or the stuff included) as Apache will block it
#        until after the user is authenticated (for example, fancy gifs)
#########################################################################
from hashlib import md5
from urllib import response
from common_func import *

def login(request):
    myhost = request['HTTP_HOST']
    domainPieces = myhost.splite(".")
    numDomains = len(domainPieces)
    domain = f"{domainPieces[numDomains - 2]}.{domainPieces[numDomains - 1]}"

    emailCookie = 'GUIAuth'
    secureCookie = 'GoogleAuth'
    loggedIn = 0
    secret_word = 'B1nar,ytR33'
    
    # Message text line on GUI
    msg = ""

    if request['access_password']:
        request['access_username'] if request['access_username'] else ''
        passwd = request['access_password']

        # Get the locale
        here = getLocale()
        if here == 'Kanata':
            site = "138.120.178.252"
        
        if here == "MtnView":
            site = "sso.mv.usa.alcatel.com:443"
        ldap = {}
        if here == "NuageMv" or here == "NuageAnt" or here == "NuageRa" or here == "NuageBa" or here == "NuageWf" or here == "NuageBt":
            ldap['host'] = "ldap://nuageldap1.mv.nuagenetworks.net"
            ldap['filter'] = "(&(objectClass=*)(memberof=CN=nuage-engineering,cn=groups,cn=accounts,dc=us,dc=alcatel-lucent,dc=com))"
            ldap['attr'] = array("mail")
            ldap['conn'] = ldap_connect(ldap['host'])
        
            if ldap['conn']:
                ldap['bind'] = ldap_bind(ldap['conn'], ldap['user'], passwd)
            
            site = "sso.mv.usa.alcatel.com:443"
        
        if here == "Antwerp":
            site = "138.203.16.150"
        if here == "Naperville":
            site = "135.2.40.7"
        if here == "Bratislava":
            site = "135.243.195.220"
        
        # location of the web service receptor, should be placed in the same place on every server
        location = "/authServer.php"

        # if we bind the ldap server, just proceed through ldap auth, otherwise,
        # call the web service, params are like so
        # XMLRPC_request(site, location, methodName, params, user_agent) user_agent is optional
        if ldap['bind'] is None:
            success = 1
        else:
            ldap['result'] = ldap_search(ldap['conn'], ldap['user'], ldap['filter'], ldap['attr'])
            result=ldap_get_entries(ldap['conn'], ldap['result'])
            success=1

        if success:
            if response[0] is None:
                msg = "Incorrect Username/Password or Access Denied"
            else:
                loggedIn = 1
                emailAddress = response[1]
                # if no email address, set it to the username
                if (emailAddress == ""):
                    emailAddress = user
                msg = "Successfully Authenticated."
        else:
            msg = "Cannot communicate with authenticating web service, try again later."
    else:
        if request['secureCookie'] != '':
            # unset(user)
            c_username = {}
            c_username['cookie_hash'] = request['secureCookie'].splite(',')
            if md5(c_username[secret_word]) == cookie_hash:
                user = c_username
                loggedIn = 1
                msg = "Already Authenticated"
            else:
                loggedIn = 0
                msg = "Session Cookie no good."
    

    if loggedIn is None:
        header("HTTP/1.0 200 OK")     #Force it to be OK. Trust me.
        header("X-Username: user")

        header("X-Groups: schedules")

        if request[secureCookie] == '':
            setcookie(secureCookie, user.','.md5(user.secret_word), time() + 60 * 60 * 24 * 7, "/", domain)

        if request[emailCookie] == '':
            setcookie(emailCookie , emailAddress,                     time() + 60 * 60 * 24 * 7, "/", domain)
        
        sourcePage = request['page']

        if sourcePage != "":
            if sourcePage != "":
                if re.search('/^http[s]*:\/\//',sourcePage):
                    sourcePage = f"http://.{myhost} .{sourcePage}"
                header( "refresh: 0; url=sourcePage")
    else:
        header("HTTP/1.0 401 Unauthorized")
        if (request[secureCookie] !=''):
            setcookie(secureCookie, "user",         time() - 3600 * 25 , "/", domain)
        if (request[emailCookie] !=''):
            setcookie(emailCookie,  "$emailAddress", time() - 3600 * 25 , "/", domain)
        

            
