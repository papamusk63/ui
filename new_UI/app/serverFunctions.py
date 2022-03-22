# Assume dictionary response in all of the below functions
# CLASS serverFunctions
# DESCRIPTION - Web service functions for the testbed GUI's

from datetime import date
import sys
import socket
import os
import subprocess
import glob
import time
from pathlib import Path
from .read_masterlog2 import *
from  .common_func import *
from .globals import *

def get_hostname(request) -> str:
    myHostName = socket.gethostname().strip()
    # TODO - Not sure what a rowserver is, and if this key exists in request env.
    # fix this later
    rowserver = request.environ.get('ROWSERVER')
    if rowserver == myHostName:
        myHostName = request.environ.get('SERVER_NAME').split(".")[0]
    # else we are in a non-virtual environment -- do nothing: host var is ok as is

    return myHostName


###########################################################################
# Web Service functions
###########################################################################

###########################################################################
# NAME - func_Hello
# test Hello function
###########################################################################
def func_Hello(request, args) -> Dict:
    host = request.host
    stuffToSay = dict()
    stuffToSay['Thing1'] = f"Hello From {host}"
    stuffToSay['Version'] = sys.version
    return stuffToSay

def HTTP_Method_not_found() -> str:
    return 'This method has not been defined yet.'

def HTTP_Malformed_request() -> str:
    return 'Request Malformed.'

###########################################################################
# NAME - func_IsHttpAlive
# DESCRIPTION - If the client receives a success, HTTP is up, no need to 
# ping anymore
# takes no args
# RETURNS - irrelevant, the caller should just test for success
###########################################################################
def func_IsHttpAlive(request,args) -> Dict:
    return {}

###########################################################################
# NAME -  func_CountQueuedJobs
# DESCRIPTION - count the jobs directory queued jobs
# I changed this func a couple of time and found the quickest way is below
# even faster than the previous function listed here for easy comparison
#    $myHostName = trim(`hostname -s`);
#    $jobsDir = "/$myHostName/jobs";
#    exec("ls -d $jobsDir/[0-9]* | wc -l", $buff);
#    XMLRPC_response(XMLRPC_prepare($buff));
# this new one is 25% faster than above
# takes no args
# RETUNRS - a number
###########################################################################
def func_CountQueuedJobs(request,args) -> int:
    myHostName = get_hostname(request)
    
    try:
        jobsDir = os.readlink(f"/{myHostName}/jobs")
    except OSError:
        jobsDir = f"/{myHostName}/jobs"

    resultsDir = f"/{myHostName}/results"

    #TODO - Not sure what the below is for as well. Remove is unused
    # touch the httpActive file, temporary until a proper timeout
    # can be applied to http request (no RH9)
    Path(f'{resultsDir}/httpActive').touch()
    count = 0
    for entry in os.listdir(jobsDir):
        if os.path.isdir(os.path.join(jobsDir, entry)):
            count+=1
    
    return count
    
###########################################################################
# NAME -  func_GetPowerStatus
# DESCRIPTION - gets the content of powerstat file in jobs directory
# args - none
# RETUNRS - a dictionary, with contetnts of powerstat file
###########################################################################
def func_GetPowerStatus(request,args) -> Dict:
    myHostName = get_hostname(request)
    try:
        jobsDir = os.readlink(f"/{myHostName}/jobs")
    except OSError:
        jobsDir = f"/{myHostName}/jobs"

    resultsDir = f"/{myHostName}/results"
    ret = dict()
    ret['powerstat'] = 'unknown'
    ret['timepowerstat'] = 0

    #TODO - Not sure what the below is for as well. Remove is unused
    # touch the httpActive file, temporary until a proper timeout
    # can be applied to http request (no RH9)
    Path(f'{resultsDir}/httpActive').touch()

    powerfile = jobsDir + "/powerstat"
    if os.path.exists(powerfile):
        ret['timepowerstat'] = filemtime(powerfile)
        powerstat = file_get_contents(powerfile)
        ret['powerstat'] = powerstat
    
    return ret

###########################################################################
# NAME - func_GetJobId
# DESCRIPTION - fills an array with various job data
# no args are required
# RETURNS - a dictionary with the jobid, version, args and url for the status GUI
###########################################################################
def func_GetJobId(request, args) -> Dict:
    myHostName = get_hostname(request)
    try:
        jobsDir = os.readlink(f"/{myHostName}/jobs")
    except OSError:
        jobsDir = f"/{myHostName}/jobs"
    
    inprogress = jobsDir + "/inprogress"
    ret = dict()
    
    if os.path.exists(inprogress):
        with open(inprogress) as fd:
            lines = fd.readlines()
        for line in lines:
            line = line.strip()
            if "(submitted timestamp)" in line:
                ret['jobid'] = line[line.index(":")+2:]
            if "ollow the results" in line:
                ret['url'] = line[line.index(":")+2:]
            if "rguments passed to tests" in line:
                ret['args'] = line[line.index(":")+2:]
            if "ersion (if known)" in line:
                ret['version'] = line[line.index(":")+2:]
    
    return ret

###########################################################################
# NAME - func_GetFileReason
# DESCRIPTION - obtains the reason, text in a file if the file exists.
# Basically it will munch together the file time and the reason.
# takes in the path and the filename. Used for pause, deferredkill, etc
# Note that the path must have / (slashes) on both ends of the string
# INPUT - request, as other functions, and a tuple of all args as input
# RETURNS - the reason or nothing, in a list
###########################################################################
def func_GetFileReason(request, args) -> List:
    myHostName = get_hostname(request)
    ret = ""
    #TODO - Add the else condition below
    if len(args)==2:
        fullFileName = f"/{myHostName}{args[0]}{args[1]}"
        if os.path.exists(fullFileName):
            # get the message
            message = get_file_content(fullFileName,1).strip()
            if message=="":
                ret = f"{args[1]} file empty"
            else:
                ret = message
    return ret

###########################################################################
# NAME - func_GetFileCreateTime
# DESCRIPTION - obtains the file create time if it exists.
# takes in the path and the filename.
# Note that the path must have / (slashes) on both ends of the string
# RETURNS - the time or nothing, as a string
###########################################################################
def func_GetFileCreateTime(request, args) -> str:
    myHostName = get_hostname(request)
    ret = ""
    #TODO - Add the else condition below
    if len(args) == 2:
        fullFileName = f"/{myHostName}{args[0]}{args[1]}"
        if os.path.exists(fullFileName):
            ret = datetime.fromtimestamp(filemtime(fullFileName)).strftime("%b %d %H:%M")
    return ret


###########################################################################
# NAME - func_DoesFileExist
# DESCRIPTION - checks for existance of a file
# provide 2 args, args[0] = path, args[1] = filename
# Note that the path must have / (slashes) on both ends of the string
# RETURNS - 0 or 1
###########################################################################
def func_DoesFileExist(request, args) -> bool:
    myHostName = get_hostname(request)
    #TODO - Add error handling below
    fullFileName = f"/{myHostName}{args[0].rstrip('/')}/{args[1].strip('/')}"
    return os.path.exists(fullFileName)

###########################################################################
# NAME - func_GetFileInArray
# DESCRIPTION - fills an array for the caller with the contents of a file
# provide 2 args, args[0] = path, args[1] = filename
# Note that the path must have / (slashes) on both ends of the string
# RETURNS - a list, empty or with file contents line by line
###########################################################################
def func_GetFileInArray(request, args) -> List:
    myHostName = get_hostname(request)
    ret = []
    if len(args)==2:
        fullFileName = f"/{myHostName}{args[0]}{args[1]}"
        if os.path.exists(fullFileName):
            with open(fullFileName) as fd:
                ret = fd.readlines()
    return ret

###########################################################################
# NAME - func_GetFileElementsInArray
# DESCRIPTION - fills a dict for the caller with the contents of a file
# provide 2 args, args[0] = path, args[1] = filename
# Note that the path must have / (slashes) on both ends of the string
# RETURNS - a dictionary
# example / 
# pause my reason
# queue 0
# would return ret[pause] = my reason, and ret[queue] = 0 
# note that, this function adds the read time to element readdate, used
# to see if guid is running or not
###########################################################################
def func_GetFileElementsInArray(request, args) -> Dict:
    myHostName = get_hostname(request)
    resultsDir = f"/{myHostName}/results"
    ret = dict()

    #TODO - Not sure what the below is for as well. Remove is unused
    # touch the httpActive file, temporary until a proper timeout
    # can be applied to http request (no RH9)
    Path(f'{resultsDir}/httpActive').touch()

    if len(args)==2:
        fullFileName =  f"{args[0]}{args[1]}"
        ret = FillStructuredArray(fullFileName)
        
        ret['readdate'] = time.time()
    
    return ret

###########################################################################
# NAME - func_GetTimingInfo
# DESCRIPTION - obtain current timing information including
# ARGS - takes 1 arg, 
# RETURNS - a structure with the following
# ret['suite_time_remaining'] (for the status GUI main display)
# the rest of the information is for the waveover pop up thing on the status GUI
# ret['running_test_name']
# ret['current_suite_name']
# ret['running_test_time_remaining'] - if negative, implies overtime
# ret['comment'] - additional information if any
# Oct 09 - ssteg, simplified to call common procs and added deferrData
###########################################################################
def func_GetTimingInfo(request,args) -> Dict:
    global currentTestId
    global aTestCase
    global aTestSuite
    global aSubTest
    ret = dict()
    if len(args)==1:
        host = get_hostname(request)

        deferrData = dict()
        # do we have a deferr file?
        #TODO - The below path doesn't look good, correct it if an error is encountered
        fileToFind = "deferredKill_suite"
        fileName = f"/{host}{args[0]}{fileToFind}"
        if os.path.exists(fileName):
            deferrData['type'] = "suite"

        fileToFind = "deferredKill_test"
        fileName = f"/{host}{args[0]}{fileToFind}"
        if os.path.exists(fileName):
            deferrData['type'] = "test"
            message = get_file_content(fileName,0)
            if "afterNamedTest" in message:
                fileStuff = message.split(" ")
                deferrData['name'] = fileStuff[1]
        
        getRunInfo(host,args[0],"summary")
        ret = getTimingInfo(deferrData,aTestSuite,aTestCase)
    
    return ret

###########################################################################
# NAME - func_GetBedStatus
# DESCRIPTION - If ever a far away status GUI wants to display your local
#  testbeds, this is the only way because /usr/global/reression is 
#  different in all locales.
#  This is really only used for testing to see if my local editted GUI
#  can display and exec server functions for all testbeds around the globe
# ARGS - takes 1 arg, a list of testbed names
# RETURNS - the testbed_status structure ordered and sorted
###########################################################################
def func_GetBedStatus(request, args) -> Dict:
    ret = dict()
    test_beds = args
    states = ["idle","inprogress","paused"]
    for status in states:
        direc = f"/usr/global/regression/{status}"
        tempStatus = list()
        if os.path.exists(direc) and os.path.isdir(direc):
            for tb in test_beds:
                if os.path.exists(f"{direc}/{tb}"): #TODO - find out who creates this file as it's not aware who is using this data structure
                    tempStatus.append(tb)
            # sort so that a human can read it
            natcasesort(tempStatus)
            for tb in tempStatus:
                ret[tb] = status
    return ret

###########################################################################
# NAME - func_GetOneBedStatus
# DESCRIPTION - If ever a far away status GUI wants to display a local
#  testbed, this reads the remote /usr/global/reression.
#  Use with caution, the exception, not the rule
# ARGS - takes 1 arg, the bed_name
# RETURNS - the testbed_status of the bed_name
###########################################################################
def func_GetOneBedStatus(request, args) -> Dict:
    ret = dict()
    if len(args)==1:
        tb = args[0]
        states = ["idle","inprogress","paused"]
        for status in states:
            direc = f"/usr/global/regression/{status}"
            if os.path.exists(direc) and os.path.isdir(direc):
                if os.path.exists(f"{direc}/{tb}"):
                    ret[tb] = status
                    break
    return ret

##########################################################################
# Name - func_GetUserJobs
# Description - fills an array where the keys are the names of job
#   directories (as seen in /<bedname>/jobs) created by the given
#   user. The array value is the contents of the args-file, located in
#   this job folder.
# returns - job directories belonging to the given user, and the 
#               corresponding args.
##########################################################################
def func_GetUserJobs(request, args) -> Dict:
    ret = dict()
    if len(args)==1:
        user = args[0]
        ret = FillQidArray(user)
    return ret


###########################################################################
# Server Methods collection
###########################################################################

# add the methods that you want made available to this list
server_methods = dict()
server_methods['func.Hello'] = func_Hello
server_methods['func.IsHttpAlive'] = func_IsHttpAlive
server_methods['func.CountQueuedJobs'] = func_CountQueuedJobs
server_methods['func.GetPowerStatus'] = func_GetPowerStatus
server_methods['func.GetJobId'] = func_GetJobId
server_methods['func.GetFileReason'] = func_GetFileReason
server_methods['func.GetFileCreateTime'] = func_GetFileCreateTime
server_methods['func.DoesFileExist'] = func_DoesFileExist
server_methods['func.GetFileInArray'] = func_GetFileInArray
server_methods['func.GetFileElementsInArray'] = func_GetFileElementsInArray
server_methods['func.GetTimingInfo'] = func_GetTimingInfo
server_methods['func.GetBedStatus'] = func_GetBedStatus
server_methods['func.GetOneBedStatus'] = func_GetOneBedStatus
server_methods['func.GetUserJobs'] = func_GetUserJobs
server_methods['method_not_found'] = HTTP_Method_not_found
server_methods['malformed_request'] = HTTP_Malformed_request