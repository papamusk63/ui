##########################################################################
# FileName - index.py
# Base File
# To call the web service functions from REST_API.py
##########################################################################

import os
import re
import subprrocess
import platform
from datetime import datetime
from typing import *
from .globals import *

##########################################################################
# Name - FillTestbedArray
# Descritpion - fills the testbed array with each testbeds full parameter set
# NOTES - the fullFileName is the entire path with filename
#       - it expects that this file is structured like...
#[DEFAULTS]
#param5 d5
#param6 d6
#
#[TESTBEDS]
#name1 param1 t1
#name1 param2 t2
#name1 param3 t3
#name1 PROFILE profile1
#
#[PROFILES]
#profile1 param3 p3
#profile1 param4 p4
#profile1 param5 p5
#       - and it will stuff the array as so
#       aArray['<testbed>']['param'] = Value
# This will be used when the new regress.params file is activated.
# 9/19/2013 - ssteg - trimmed down to only the elements that the GUI needs
#                     because regress.params has exploded
# 10/3/2013 - ssteg - optionally only return beds in site
##########################################################################
def FillTestbedArray(fullFileName, site="0"):
    # initialize variables
    ret = dict()
    default = False
    testbeds = False
    profiles = False
    aKeep = dict()
    aDefault = dict()
    aTestbeds = dict()
    aProfiles = dict()
    # regress.params elements that the GUI requires.
    # If another element is needed, add it here.
    aKeep['IP'] = 1
    aKeep['DESCRIPTION'] = 1
    aKeep['ACCESS'] = 1
    aKeep['FLASHGUI'] = 1
    aKeep['SITE'] = 1
    aKeep['GROUPS'] = 1
    aKeep['PROFILE'] = 1
    aKeep['LOCATION'] = 1
    aKeep['GATEWAY'] = 1
    aKeep['BEDTYPE'] = 1
    aKeep['ROWSERVER'] = 1

    if os.path.exists(fullFileName):
        with open(fullFileName,'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            # get rid of blank lines and comments
            if line == "":
                continue
            
            poundIndex = line.find('#')
            if poundIndex != -1:
                if poundIndex == 0:
                    continue
                else:
                    # in line comments, strip from the # to the end of the line
                    line = line[poundIndex:]
            
            # if not one we know about, stop until we do
            #TODO - Something seems wrong in the below continue statements, there shouldn't be an if comparing the three if we're simply continuing with the for loop
            if re.match('^\[[a-zA-Z0-9]', line): #TODO - check if regex is correct
                default = False
                testbeds = False
                profiles = False
                if "[DEFAULTS]" in line:
                    # found beginning of default section, set the flags
                    default = True
                    testbeds = False
                    profiles = False
                    continue
                
                if "[TESTBEDS]" in line:
                    # found beginning of testbeds section, set the flags
                    default = False
                    testbeds = True
                    profiles = False
                    continue
                
                if "[PROFILES]" in line:
                    # found beginning of profiles section, set the flags
                    default = False
                    testbeds = False
                    profiles = True
                    continue
                
            

            if default or profiles or testbeds:
                value2 = ""
                aLineStuff = line.split(" ")
                counter = 0
                for value in aLineStuff:
                    if value == "":
                        continue
                    
                    counter+=1
                    if counter == 1:
                        element = value
                    elif counter == 2:
                        element2 = value
                    else:
                        value2 += f"{value} "
                    
                
                value2 = value2.strip()

                # only store regress.params data that is required by the GUI
                if element2 not in aKeep:
                    continue
                
                
                if default:
                    if element2 in aDefault:
                        aDefault[element2] = aDefault[element2] + f" {value2}"
                    else:
                        aDefault[element2] = value2
                    
                
                if testbeds:
                    if element in aTestbeds:
                        if element2 in aTestbeds[element]:
                            aTestbeds[element][element2] = aTestbeds[element][element2] + f" {value2}"
                        else:
                            aTestbeds[element][element2] = value2
                    else:
                        aTestbeds[element] = dict()
                        aTestbeds[element][element2] = value2
                    
                
                if profiles:
                    if element in aProfiles:
                        if element2 in aProfiles[element]:
                            aProfiles[element][element2] = aProfiles[element][element2] + f" {value2}"
                        else:
                            aProfiles[element][element2] = value2
                    else:
                        aProfiles[element] = dict()
                        aProfiles[element][element2] = value2
                    
                
            
        

        # ok, done parsing, now need to create the ret multi-dimensional array in the order
        # of default first, overwritten by the profile, overwritten by testbed specific
        for key in aTestbeds:
            if site == "0" or aTestbeds[key]['SITE'] == site:
                # here I am going around for each testbed, first set the defaults
                for defaultKey in aDefault:
                    if key not in ret:
                        ret[key] = dict()
                    ret[key][defaultKey] = aDefault[defaultKey]
                
                # here we are looking for the profiles only and setting those parameters
                if 'PROFILE' in aTestbeds[key]:
                    # support for multiple profiles, last profile wins for duplicate profile entries
                    aBedProfiles = aTestbeds[key]['PROFILE'].split(" ")
                    for prof_val in aBedProfiles:
                        if prof_val in aProfiles:
                            for key3 in aProfiles[prof_val]:
                                ret[key][key3] = aProfiles[prof_val][key3]
                    
                
                # here we are going around foreach parameter of a particular testbed
                # but if we find a profile, ignore it as we already set them above
                for key2 in aTestbeds[key]:
                    if key2 == "PROFILE":
                        continue
                    
                    ret[key][key2] = aTestbeds[key][key2]
                
            else:
                continue
        
    return ret

def make_pop_up(ps): #This function implemented in jobs_index.py
    pass

def htmlspecialchars(text): #Replace special characters
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

def array_multisort(arr,sort_method,rest): #This function implemented in jobs_index.py
    pass

def filemtime(filename): #Returns time of last modification of the specified path
    return os.path.getmtime(filename)


##########################################################################
# Name - get_file_content
# ssteg - added optional filetime
##########################################################################
def get_file_content(filename,date=0):
    with open(filename) as f:
        lines = f.readlines()
    toReturn = ""
    for line in lines:
        c = line.strip()
        if c:
            if toReturn:
                toReturn += "<br/>" + c
            else:
                toReturn += c
    if date!=0:
        fileTime = datetime.fromtimestamp(filemtime(filename)).strftime("%b %d %H:%M")
        toReturn = f"[{fileTime}] {toReturn}"
    return toReturn

def file_get_contents(filename):
    with open(filename,'r') as fd:
        return fd.read()

##########################################################################
# Name - get_full_file_content
# return an array with the optional filetime included with element 0
# each line of the file will be another element in the structure
##########################################################################
def get_full_file_content(fn,date=0):
    with open(fn,'r') as fd:
        ret = fd.readlines()
    if date != 0:
        fileTime = datetime.fromtimestamp(filemtime(fn)).strftime("%b %d %H:%M")
        ret[0] = f"[{fileTime}] {ret[0]}"
    return ret

##########################################################################
# Name - pingip
# ping ip of a host
##########################################################################
def pingip(ip):
    ping_command = ['ping', '-c', '1', '-w', '1', '-q', ip]
    ping_output = subprocess.run(ping_command,stdout=subprocess.PIPE)
    return ping_output.returncode
##########################################################################
# Name - isOnLine
# Descritpion - determines if http is up or not
# returns True or False
##########################################################################
def isOnline(ip):
    value = False #Default
    success, response = MAKE_API_CALL(ip, serverLocation, 'func.IsHttpAlive')
    if success:
        value = True
    return value

##########################################################################
# Name - getLocale
# Descritpion - determines machine location
# returns - the location string
##########################################################################
def getLocale():
	localeFile = '/usr/global/regression/LOCALE'
    if os.path.exists(localeFile):
        return file_get_contents(localeFile)

##########################################################################
# Name - doesFileExist
# Descritpion - check if a file exists or not on a remote machine
# uses web method
# NOTES - the path param requires slashes on both ends
# returns - True or False in element 0 of an array
##########################################################################
def doesFileExist(host, path, file):
    ret = False
    success, response = MAKE_API_CALL(host, serverLocation, func.DoesFileExist, path, file)
    if success:
        if response == 1:
            ret = True
    return ret

##########################################################################
# Name - GetFileInArray
# Descritpion - fills an array with the contents of a remote file
# uses web method
# NOTES - the path param requires slashes on both ends
#       - large files are not intended to be passed this way, if you need
#       the contents of a large file, make the remote machine do the work
#       and only pass back the answer.
# returns - an array with each element being a line of remote file
##########################################################################
def GetFileInArray(host, path, file):
    ret = [] #Create empty list
    success, response =  MAKE_API_CALL(host, serverLocation, 'func.GetFileInArray',path, file)
    if success:
        ret = response
    return ret

##########################################################################
# Name - GetFileCreateTime
# Descritpion - fills an array with the creatiion timestamp of $file
# uses web method
# NOTES - the path param requires slashes on both ends
# returns - an array with element 0 being the time
##########################################################################
def GetFileCreateTime(host, path, file):
    ret = [] #Create empty list
    success, response = MAKE_API_CALL(host, serverLocation, 'func.GetFileCreateTime', path, file)
    if success:
        ret = response
    return ret

##########################################################################
# Name - get_first_available (Renamed fucntion in common_func.php - get_available )
# Descritpion - figures which remote machine is available
# returns - the ip of a remote machine or nothing
##########################################################################
def get_first_available(aTbs):
    for tb, params in aTbs.items():
        if pingip(params.get('IP')) == "0":
            return(params.get('IP'))

##########################################################################
# Name - FillStructuredArray
# Descritpion - fills an array with the contents of a file
# NOTES - the fullFileName is the entire path with filename
#       - it expects that a file is structured like
#       Word Value
#       - and it will stuff the array as so
#       aArray("Word") = Value
#       - only one Word Value per line
##########################################################################
def FillStructuredArray(fullFileName):
    ret = {}
    if os.path.exists(fullFileName):
        lines = open(fullFileName).readlines()
        for line in lines:
            line = line.strip()
            if line.isspace() or len(line) == 0:
                continue
            spaceIndex = line.find(" ")
            if spaceIndex != 0:
                element = line[0:spaceIndex]
                value = line[spaceIndex + 1:]
            else:
                element = line
                value = ""
            ret[element] = value
    return ret

##########################################################################
# Name - natksort
# Descritpion - natural order sorts based on keys, not contents
##########################################################################
def natksort(array: OrderedDict) -> OrderedDict:
    '''
    sort a dictionary based on natural order
    e.g. Input = (
    [IMG0.png] => 0
    [img12.png] => 1
    [img10.png] => 2
    [img2.png] => 3
    [img1.png] => 4
    [IMG3.png] => 5
    )
    Output = (
    [IMG0.png] => 0
    [img1.png] => 4
    [img2.png] => 3
    [IMG3.png] => 5
    [img10.png] => 2
    [img12.png] => 1
    )
    '''
    sorted_keys_arr = natcasesort(array.keys())
    results_arr = OrderedDict((key,array[key]) for key in sorted_keys_arr)
    return results_arr

def atoi(text: str) -> Union[int,str]:
    return int(text) if text.isdigit() else text.lower()

def natural_keys(text: str) -> List:
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''    
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def natcasesort(array: List) -> List:
    return sorted(array,key=natural_keys)
##########################################################################
# Name - FillQidArray
# Description - fills an array where the keys are the names of job
#   directories (as seen in /<bedname>/jobs) created by the given
#   user. The array value is the contents of the args-file, located in
#   this job folder.
# uses web method
# returns - an array with each element being formed like
# ret[element] = value
##########################################################################
def FillQidArray(user):
    ret = {}
    myHostName = platform.node()
    list_all_files = os.listdir("/" + myHostName + "/" + "jobs")
    if user == "regress":
      for jobDir in list_all_files:
        if  "sr-test-infra" in jobDir or "regressiondb" in jobDir:
          open_file = open("/" + myHostName + "/" + "jobs" + jobDir + "/" + "args", "r")
          ret[jobDir]=open_file.read()
          open_file.close()
    else:
      get_email = subprocess.run(['/usr/global/bin/usertoemail.sh', user], stdout=subprocess.PIPE)
      email = get_email.stdout.decode("utf-8")
      myName = email.split('@')[0]
      for jobDir in list_all_files:
        if myName in jobDir:
            open_file = open("/" + myHostName + "/" + "jobs" + jobDir + "/" + "args", "r")
            ret[jobDir]=open_file.read()
            open_file.close()
    return ret


if __name__ == "__main__":
    #Test FTA
    rp = "/usr/global/bin/regress.params"
    print(FillTestbedArray(rp))
