# TODO: add memeory limitation from line 1 - 5
import os
import json
import html
import re
import platform
import json
import time
from urllib.parse import urlparse
from .time_left import *
from .globals import *
from .common_func import *

aTestSuite = None
aTestClass = None
aTestCase = None
aSubTest = None
currentTestId = None
currentSubTestName = None
currentTestClass = None

##################################################################################################
# NAME - getRunInfo
# DESCRIPTION - parses thorugh intended, completed and masterlog.txt to get the current state
# of a particular job and stuffs the results into 3 structures...
# aTestSuite
# aTestCase
# aSubTest
# parameters - $path is the path to the results dir like /results/2009/Month_10/Oct_26/00:00:moretime/
#              $detail can be - "summary" or "detail", detail adds url links
# NOTE - $host should not be global, it is called remotely and locally (web methods)
# NOTE 2 - to get a complete picture of all pass fail counts, you must call this in detail mode
##################################################################################################
def getRunInfo(host,path,detail): #completed
    global aTestSuite
    global aTestClass
    global aTestCase
    global currentTestId
    global currentSubTestName
    global currentTestClass

    if aTestCase is None:
        aTestCase = dict()
    if aTestClass is None:
        aTestCase = dict()
    currentSubTestName = ""
    filename = "intendedTestList"
    intended = f"/{host}{path}{filename}"
    if getTestFramework(host,path) == 'pygash':
        intended = f"/{host}{path}pygash_logs/{filename}"
    
    filename2 = "completedTestList"
    completed = f"/{host}{path}{filename2}"
    arr = [intended, completed]
    for fileName in arr:
        intended = False
        if "intended" in fileName:
            intended = True
        test_num = 0
        suite_num = 0
        class_num = 0
        if os.path.exists(fileName):
            with open(fileName) as fd:
                for line in fd:
                    line = line.strip()
                    if line == "":
                        continue
                    if re.match('^::TestClass::(.*) (.*)/',line):
                        lineParts = re.match('^::TestClass::(.*) (.*)/',line)
                        # this is pygash specific
                        currentTestClass = lineParts[1]
                        class_num += 1
                        if intended:
                            aTestClass[suite_num][class_num]['name']= currentTestClass
                    elif not re.match('^::TestSuite::(.*) (.*)/',line):
                        test_num+=1
                        lineStuff = line.split(" ",1)
                        name = lineStuff[0]
                        # if there is a ::TestSuite at the beginning of the name, rip some off
                        if "::TestSuite" in name:
                            name = name[name.find("::TestSuite"):].lstrip("::Test")

                        if intended:
                            aTestCase[test_num]['name'] = name
                            aTestCase[test_num]['suite'] = suite_num
                            aTestCase[test_num]['test_class'] = class_num
                            if "unknown" not in lineStuff[1]:
                                aTestCase[test_num]['est'] = format_time(lineStuff[1])
                            else:
                                aTestCase[test_num]['est'] = 'unknown'
                        else:
                            if "Cleanup" in name:
                                finIndex: bool = findTestIndex(name, test_num)
                                if finIndex != False:
                                    test_num = finIndex
                            
                            if "aborted" not in lineStuff[1]:
                                aTestCase[test_num]['act'] = format_time(lineStuff[1])
                            else:
                                aTestCase[test_num]['act'] = "aborted"
                            
                            aTestCase[test_num]['endtime'] = lineStuff[1][lineStuff[1].rfind(" "):]
                            currentTestId = test_num
                    else: 
                        lineParts = re.match('^::TestSuite::(.*) (.*)/',line)
                        suite_num+=1
                        class_num = 0
                        currentTestClass = ""
                        if intended:
                            aTestSuite[suite_num]['name'] = lineParts[1]
                        else:
                            aTestSuite[suite_num]['starttime'] = lineParts[2]
    addSuiteTimingInfo()
    addClassTimingInfo()
    if detail == "detail":
        getDetailedResults(host,path)
        addUrlLinks(host,path)
    else:
        try:
            # the current running test 'could be' the next test after the last run one
            # a bit of a risk, done so we don't have to parse the masterlog for the status GUI
            currentTestId+=1
        except:
            pass



#####
# Extract TestCaseName and SubtestName
# 
######
def extractTestNames(name):	#completed	

    namearr = name.split('::')
    testcaseNameArray = namearr[0:2]
    subtestNameArray = namearr[-1] 
    testcaseName = ".".join(testcaseNameArray)
    subtestname = "".join(subtestNameArray)
    return [testcaseName, subtestname]



def getRunInfoForPygash(host, path): #completed
    global aTestSuite
    global aTestCase
    global aSubTest
    global currentTestId
    global currentSubTestName

    uniqTestCase = {}
    if aTestSuite is None:
        aTestSuite: Dict = dict()
    file = "summary.json"
    fileName = f"/{host}{path}pygash_logs/{file}"
    if (os.path.exists(fileName)):
        str_data = file_get_contents(fileName)
        data: Dict[str,Dict[str,str]] = json.loads(str_data)
        suite_count = 0 
        testcase_count = 0 
        subtest_count = 0
        for suite_info_key, suite_info_value in data.items():
            suite_count+=1
            current_suite = suite_info_key
            actual = 0
            result = "unknown"
            testRan = 0
            starttime = 0
            subTestName = ""
            subindex = ""
            aTestSuite[suite_count]["name"] = current_suite
            aTestSuite[suite_count]["act"] = actual
            aTestSuite[suite_count]["est"] = get_estimate_pygash(current_suite)

            for suite_params_key, suite_params_value in suite_info_value.items():
                if suite_params_key == "time":
                    aTestSuite[suite_count]['act'] = round(suite_params_value,2) 
                elif suite_params_key == "result":
                    aTestSuite[suite_count]['result'] = suite_params_value.upper() #Check the type of suite_params_value
                elif suite_params_key == "state":
                    aTestSuite[suite_count]['state'] = suite_params_value
                elif suite_params_key == "starttime":
                    aTestSuite[suite_count]['starttime'] = round(suite_params_value)
                    aTestSuite[suite_count]['testRan'] = 1
                elif suite_params_key=="tests":
                    endtime = 0
                    outcome = "unknown"
                    for testrecord_key,testrecord_value in suite_params_value.items():
                        error = ""
                        for subtestparam_key, subtestparam_value in testrecord_value.items():
                            if subtestparam_key == 'name':
                                testcaseName, subTestName = extractTestNames(subtestparam_value)
                                if uniqTestCase not in testcaseName:
                                    testcase_count+=1
                                    subtest_count = 1
                                    aTestCase[testcase_count]["act"] = 0
                                    endtime = 0
                                    outcome = "unknown"
                                    uniqTestCase[testcaseName] = testcase_count
                                    aTestCase[testcase_count]["name"] = testcaseName
                                    aTestCase[testcase_count]["est"] = get_estimate_pygash(testcaseName)
                                    aTestCase[testcase_count]["suite"] = suite_count
                                    aTestCase[testcase_count]["lineNum"] = 1
                                else:
                                    subtest_count+=1
                                
                                subindex = f"{testcase_count}.{subtest_count}"
                                aSubTest[subindex]["name"] = subTestName
                                aSubTest[subindex]["test"] = str(testcase_count)
                                aSubTest[subindex]["est"] = get_estimate_pygash(subTestName)
                                aSubTest[subindex]["suite"] = suite_count

                            if subtestparam_key == 'time':
                                aSubTest[subindex]["act"] = round(subtestparam_value,2)
                            if subtestparam_key == 'state':
                                if subtestparam_value == 'running':
                                    currentSubTestName = subTestName
                                    currentTestId = testcase_count

                        for subtestparam_key, subtestparam_value in testrecord_value.items():
                            if subtestparam_key == 'error':
                                error = subtestparam_value
                        
                        for subtestparam_key, subtestparam_value in testrecord_value.items():
                            if subtestparam_key == 'state':
                                aSubTest[subindex]["state"] = subtestparam_value
                            if subtestparam_value == 'not run' or subtestparam_value == 'skipped':
                                aSubTest[subindex]["result"] = "NOT_RUN"
                        
                        for subtestparam_key, subtestparam_value in testrecord_value.items():
                            if subtestparam_key == 'outcome':
                                outcome = subtestparam_value.upper()
                                if "result" not in aSubTest[subindex]:
                                    aSubTest[subindex]["result"] = subtestparam_value.upper()
                                if aSubTest[subindex]["result"] == 'FAILED':
                                    aSubTest[subindex]["error"] = error
                                
                                if "result" not in aTestCase[testcase_count]:
                                    aTestCase[testcase_count]["result"] = outcome.upper()
                                else:
                                    if aTestCase[testcase_count]["result"] != 'FAILED':
                                        if outcome == 'FAILED':
                                            aTestCase[testcase_count]["result"] = outcome.upper()
                                        if outcome == 'PASSED':
                                            aTestCase[testcase_count]["result"] = outcome.upper()

                        for subtestparam_key, subtestparam_value in testrecord_value.items():
                            if subtestparam_key == 'endtime':
                                if int(subtestparam_value)>endtime:
                                    aTestCase[testcase_count]["endtime"] = int(subtestparam_value)
                                    endtime = int(subtestparam_value)
                            if subtestparam_key == 'time':
                                aTestCase[testcase_count]["act"] += round(subtestparam_value, 2)



def get_estimate_pygash(entity): #completed
    host = platform.node()
    regress_data_file = f"/{host}/regress_data/pygashTestDurations.json"
    found = False
    found_value = 0
    data = []
    if os.path.exists(regress_data_file):
        with open(regress_data_file) as str_file:
            str_data = str_file.read()
            if str_data:
                data = json.loads(str_data)
                for k,v in enumerate(data):
                    if k == entity:
                        found = True
                        found_value = data[entity]
                if not found:
                    return 0
                else:
                    return str(round((float(found_value), 2)))
            else:
                return 0

##################################################################################################
# NAME - addSuiteTimingInfo
# DESCRIPTION - adds up suite times based upon test times, both actual and estimated
##################################################################################################

def addSuiteTimingInfo(): #completed
    global aTestSuite
    global aTestCase
    for key2 in aTestCase.keys():
        suite = aTestCase[key2]['suite']
        if suite not in aTestSuite:
            aTestSuite[suite] = {}
        
        if aTestSuite[suite].get('est') is None:
            aTestSuite[suite]['est'] = 0
        if aTestCase[key2].get('est') is not None:
            aTestSuite[suite]['est'] += aTestCase[key2]['est']

        if aTestSuite[suite].get('act') is None:
            aTestSuite[suite]['act'] = 0
        if aTestCase[key2].get('act') is not None:
            aTestSuite[suite]['act'] += aTestCase[key2]['act']
        


##################################################################################################
# NAME - addClassTimingInfo
# DESCRIPTION - adds up class times based upon test times, both actual and estimated
##################################################################################################
def addClassTimingInfo(): #completed
    global aTestClass
    global aTestCase
    for key2 in aTestCase.keys():
        test_class_id = aTestCase[key2]['test_class']
        suite = aTestCase[key2]['suite']
        if suite in aTestClass and test_class_id in aTestClass[suite] and aTestClass[suite][test_class_id].get('name'):
            if aTestClass[suite][test_class_id].get('est') is None:
                aTestClass[suite][test_class_id]['est'] = 0
            if aTestCase[key2].get('est') is not None:
                aTestClass[suite][test_class_id]['est'] += aTestCase[key2]['est']

            if aTestClass[suite][test_class_id].get('act') is None:
                aTestClass[suite][test_class_id]['act'] = 0
            if aTestCase[key2].get('act') is not None:
                aTestClass[suite][test_class_id]['act'] += aTestCase[key2]['act']
        
        if aTestClass[suite][test_class_id].get('result') is None:
            aTestClass[suite][test_class_id]['result'] = "PASSED"
        
    


##################################################################################################
# NAME - getDetailedResults
# DESCRIPTION - adds the ['result'] to the Suite and testcase and creates the subtest structure
# if there are any subtests
# NOTE - must call getRunInfo first
##################################################################################################
def getDetailedResults(host, path): #TODO - Break this down into smaller functions
    global firstError
    global currentTestId
    global aTestSuite
    global aTestCase
    global aTestClass
    global currentSubTestName
    global aSubTest

    tempError = ""
    tempLineNum = 0
    firstError = ""
    firstSubtestError = ""
    test_num = 0
    line_count = 0
    file = "masterlog.txt"
    fileName = f"/{host}{path}{file}"

    if (os.path.exists(fileName)):
        # don't do a file command for large files, takes too much memory, masterlog can be huge
        with open(fileName) as handle:
            for line in handle:
                line = line.strip()
                line = htmlspecialchars(line)
                line_count+=1
                if (line == ""):
                    continue

                if re.match('^MASTER: BEGIN ::TestDB::TestSuite(.*)', line):
                    lineStuff = re.match('^MASTER: BEGIN ::TestDB::TestSuite(.*)', line).groups()
                    currentSubTestName = ""
                    firstSubtestError = ""
                    # if we have an error left in the bank, it must be from the previous customer
                    if tempError != "": 
                        failTheTest(test_num, tempError, tempLineNum)
                        tempError = ""
                        #$firstSubtestError = "";
                    nameStuff: List = lineStuff[1].split("::")
                    if (nameStuff[0] != ""): 
                        test_num += 1
                        # what if all of a sudden a Cleanup comes out of sequence, better sync up
                        if "Cleanup" in nameStuff[0]:
                            myName = f"Suite{lineStuff[1]}"
                            finIndex = findTestIndex(myName, test_num)
                            if finIndex != False: #TODO - Fix the return value of findTestIndex first
                                test_num = finIndex
                            
                        
                        currentTestId = test_num
                        currentName = aTestCase[test_num]['name']
                        aTestCase[test_num]['lineNum'] = line_count
                
                elif re.match('^MASTER: BEGIN ::TestDB::TestCase::(.*)', line):
                    lineStuff = re.match('^MASTER: BEGIN ::TestDB::TestCase::(.*)', line).groups()
                    currentSubTestName = ""
                    firstSubtestError = ""
                    tempName = lineStuff[1]
                    finIndex = findTestIndex(tempName, test_num)
                    # it better exist, else ignore it, must be some test out of the blue
                    if finIndex != False:
                        # if we have an error left in the bank, it must be from the previous customer
                        if tempError != "":
                            failTheTest(test_num, tempError, tempLineNum)
                            tempError = ""
                            #$firstSubtestError = "";
                        
                        test_num+=1
                        numSubTest = 0
                        currentTestId = test_num
                        currentName = aTestCase[test_num]['name']
                        aTestCase[test_num]['lineNum'] = line_count
                
                elif re.match('^MASTER: END ::TestDB::TestSuite(.*)', line):
                    lineStuff = re.match('^MASTER: END ::TestDB::TestSuite(.*)', line).groups()
                    currentSubTestName = ""
                    firstSubtestError = ""
                    numSubTest = 0
                    nameStuff = lineStuff[1].split("::")
                    if nameStuff[0] == "Setup":
                        if tempError != "":
                            failTheTest(test_num, tempError, tempLineNum)
                            tempError = ""
                            #$firstSubtestError = "";
                        
                        if aTestCase[test_num].get('result') is not None:
                            aTestCase[test_num]['result'] = "PASSED"
                            # inform the suite that something ran
                            aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                        
                    
                    if nameStuff[0] == "Cleanup":
                        if tempError != "":
                            failTheTest(test_num, tempError, tempLineNum)
                            tempError = ""
                        
                        if aTestCase[test_num].get('result') is not None:
                            aTestCase[test_num]['result'] = "PASSED"
                            # inform the suite that something ran
                            aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                        
                        if aTestSuite[aTestCase[test_num]['suite']].get('result') is not None:
                            aTestSuite[aTestCase[test_num]['suite']]['result'] = "PASSED"
                
                elif re.match('CRIT: (.*)', line):
                    lineStuff = re.match('CRIT: (.*)', line).groups()
                    # bank the first error, don't know who it's for yet
                    if tempError == "":
                        tempError = "CRIT: $lineStuff[1]"
                        tempLineNum = line_count
                        if firstError == "":
                            firstError = lineStuff[1]
                        
                elif re.match('ERROR: (.*)', line):
                    lineStuff = re.match('ERROR: (.*)', line).groups()
                    # bank the first error, don't know who it's for yet
                    if tempError == "":
                        tempError = "ERROR: $lineStuff[1]"
                        tempLineNum = line_count
                        if firstError == "":
                            firstError = lineStuff[1]
                # the . is because we see either upper or lower case of the c
                elif re.match('^(?:MASTER: )?RESULT: (\S+): Test .ase(\s+)(\S+)', line):
                    lineStuff = re.match('^(?:MASTER: )?RESULT: (\S+): Test .ase(\s+)(\S+)', line).groups()
                    if "$lineStuff[3]" == "$currentName":
                        # there can be no more subtests
                        numSubTest = 0
                        if firstSubtestError != "":
                            aTestCase[test_num]['error'] = firstSubtestError
                            lineStuff[1] = "FAILED"
                            aTestCase[test_num]['result'] = lineStuff[1]
                            # inform the suite that something ran
                            aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                            aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['testRan'] = 1
                            aTestCase[test_num]['url'].append(f"masterlog.html|masterlog.html#{firstSubtestErrorLineNum}")
                            firstSubtestError = ""
                            tempError = ""
                        elif tempError != "":
                            aTestCase[test_num]['error'] = tempError
                            lineStuff[1] = "FAILED"
                            aTestCase[test_num]['result'] = lineStuff[1]
                            # inform the suite that something ran
                            aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                            aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['testRan'] = 1
                            aTestCase[test_num]['url'].append("masterlog.html|masterlog.html#$tempLineNum")
                            tempError = ""
                        else:
                            aTestCase[test_num]['result'] = lineStuff[1]
                            # inform the suite that something ran
                            aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                            aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['testRan'] = 1
                            if lineStuff[1] == "FAILED":
                                aTestCase[test_num]['url'].append(f"masterlog.html|masterlog.html#{line_count}")
                    else:
                        numSubTest+=1
                        subTestNum = f"{test_num}.{numSubTest}"
                        if tempError != "":
                            aSubTest[subTestNum]['error'] = tempError
                            if firstSubtestError == "":
                                firstSubtestError = tempError
                                firstSubtestErrorLineNum = tempLineNum
                            
                            lineStuff[1] = "FAILED"
                            tempError = ""
                        else:
                            tempLineNum = line_count
                    
                        preName = aTestCase[test_num]['name']
                        aSubTest[subTestNum]['name'] = f"{preName}.{numSubTest}"
                        aSubTest[subTestNum]['test'] = test_num
                        aSubTest[subTestNum]['result'] = lineStuff[1]
                        if lineStuff[1] == "FAILED":
                            aTestCase[test_num]['result'] = lineStuff[1]
                            # inform the suite that something ran
                            aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                            aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['testRan'] = 1
                            aSubTest[subTestNum]['url'].append("masterlog.html|masterlog.html#$tempLineNum")                               
                    if lineStuff[1] == "FAILED":
                        aTestSuite[aTestCase[test_num]['suite']]['result'] = "FAILED"
                        aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['result'] = "FAILED"
                elif re.match('^(?:MASTER: )?SUB_RESULT: (\S+): (.*)/', line):
                    lineStuff = re.match('^(?:MASTER: )?SUB_RESULT: (\S+): (.*)/', line).groups()
                    numSubTest+=1
                    subTestNum = f"{test_num}.{numSubTest}"
                    if tempError != "":
                        aSubTest[subTestNum]['error'] = tempError
                        if firstSubtestError == "":
                            firstSubtestError = tempError
                            firstSubtestErrorLineNum = tempLineNum
                        
                        lineStuff[1] = "FAILED"
                        tempError = ""
                    else:
                        tempLineNum = line_count
                    
                    # people only want to see the subtest name, not the parent too
                    # $aSubTest[$subTestNum]['name'] = substr($lineStuff[2], (strlen($aTestCase[$test_num]['name']) + 1));
                    # using string replace instead of extracting substr. above line is the original code
                    aSubTest[subTestNum]['name'] = lineStuff[2].replace(aTestCase[test_num]['name'] + ".", '')
                    aSubTest[subTestNum]['test'] = test_num
                    aSubTest[subTestNum]['result'] = lineStuff[1]
                    if lineStuff[1] == "FAILED":
                        aSubTest[subTestNum]['url'].append("masterlog.html|masterlog.html#$tempLineNum")
                        aTestCase[test_num]['result'] = lineStuff[1]
                        # inform the suite that something ran
                        aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
                        aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['testRan'] = 1
                        aTestSuite[aTestCase[test_num]['suite']]['result'] = lineStuff[1]
                        aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['result'] = lineStuff[1]
                elif re.match('^SUB_START: (.*)',line):
                    lineStuff = re.match('^SUB_START: (.*)',line).groups()   
                    currentSubTestName = lineStuff[1][len(aTestCase[test_num]['name']) + 1:]
        # it just ended somehow with an error in the bank, fail the last test and suite I guess
        if tempError != "":
            failTheTest(test_num, tempError, tempLineNum)


################################################################################
# Name - failTheTest
# Description - set the appropriate elements to fail a test
#               created to simplify the getting details
################################################################################
def failTheTest(test_num, tempError, tempLineNum): #completed
    aTestCase[test_num]['error'] = tempError
    aTestCase[test_num]['result'] = "FAILED"
    aTestCase[test_num]['url'].append(f"masterlog.html|masterlog.html#{tempLineNum}")
    aTestSuite[aTestCase[test_num]['suite']]['result'] = "FAILED"
    aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['result'] = "FAILED"
    # inform the suite that something ran
    aTestSuite[aTestCase[test_num]['suite']]['testRan'] = 1
    aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['testRan'] = 1


################################################################################
# Name - determineVer
# Description - was index.html created with the old or new createReport?
# Note - there should be a better way. This is looking for line_num anchor
################################################################################
def determineVer(host, path):   #completed
    ret = 0
    file = f"masterlog.html"
    filename = f"/{host}{path}{file}"
    if os.file.exists(filename):
        with open(filename) as temp:
            for line in temp:
                line = line.strip()
                if not line:
                    continue
                if re.match(r'^<A NAME="[0-9]*"', line):
                    ret = 1
    return ret


####################################################################################################
# NAME - getTestConsoleIndx
# DESCRIPTION - finds what is the index of the test_console.X.html file containing the test_num test
# parameters - $test_num is the test run number
####################################################################################################
def getTestConsoleIndx(test_num):  #completed
    """
    DESCRIPTION - 
    INPUT - 
    OUTPUT FORMAT - 
    """
    global aTestCase
    indx_this = 0
    key_indx = 0
    for temp in aTestCase:
        key = temp[0]
        try:
            aTestCase[key]['console_indx']
            indx_this = aTestCase[key]['console_indx']
            key_indx = key
        except:
            pass        
        if key_indx > test_num:
            indx_this -= 1
            break
        if key_indx == test_num:
            break
        
    
    # check if index.html was created with an older version of CreateReport.pl
    # with test_console not being fragmented
    if indx_this == 0:
        indx_this = "none"
    
    return indx_this


################################################################################
# Name - addUrlLinks
# Description - parses index.html filling in links to ESR and test_console logs
################################################################################
def addUrlLinks(host, path):  # TODO - fix the unrecognised variable test_num
    global aTestSuite
    global aTestCase
    global runStatus
    file = "masterlog.html"
    file2 = "index.html"
    fileName = f"/{host}{path}{file}"
    fileName2 = f"/{host}{path}{file2}"
    if (os.file.exists(fileName)):
        flag = 0
        flag2 = 0
        flag0 = 1
        indx = 0
        failed_t = ""
        with open(fileName2) as readFile:
            for line in readFile:
                line = line.strip()
                if line == "":
                    continue
                
                # step 1: finding the first test's number and index of each test_console.X.html file
                if flag0 and re.match('<input type="hidden" id="indexes" value="([0-9]*)"' , line):
                    matches = re.match('<input type="hidden" id="indexes" value="([0-9]*)"' , line).groups()
                    key = matches[1]
                    indx =+ 1
                    aTestCase[key]['console_indx'] = indx
                    continue
                
                # step 2: go to the next step
                if (re.match('Console output for',line)):
                    flag0 = 0
                    continue
                
                # getting the overall status of the regression job
                if re.match('Overall Regression Status: (.*)\<', line):
                    runStatus = re.match('Overall Regression Status: (.*)\<', line).groups()[1]
                
                # step 3: If there are links for the failed tests, go to the next step
                if re.match('Hyperlinks for failed tests',line):
                    flag = 1
                    flag2 = 0
                    continue
                
                # step 4: matches the test that are reported to be failed,
                if flag and re.match('\<input type=\"hidden\" value=\"([0-9]*)\"\>' , line):
                    matches = re.match('\<input type=\"hidden\" value=\"([0-9]*)\"\>' , line).groups()
                    key = matches[1]
                    aTestCase[key]['result'] = "FAILED"
                    aTestSuite[aTestCase[key]['suite']]['result'] = "FAILED"
                    aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['result'] = "FAILED" #TODO - test_num is undefined yet
                    flag = 2
                
                if flag==2 and re.match('\<LI\>\<A HREF=\"(.*)\"\>(.*)\<\/A\>', line):
                    matches = re.match('\<LI\>\<A HREF=\"(.*)\"\>(.*)\<\/A\>', line).groups()
                    aTestCase[key]['url'].append(f"{matches[2]}|{matches[1]}")
                
                # don't forget failed bootup sequences, report under test1 (key)
                if (re.match('Hyperlinks for failed boot sequences',line)):
                    flag2 = 2
                    flag = 0
                    key = 1
                    aTestCase[key]['result'] = "FAILED"
                    aTestSuite[aTestCase[key]['suite']]['result'] = "FAILED"
                    aTestClass[aTestCase[test_num]['suite']][aTestCase[test_num]['test_class']]['result'] = "FAILED"
                    continue
                
                if flag2==2 and re.match('\<LI\>\<A HREF=\"(.*)\"\>(.*)\<\/A\>', line):
                    matches = re.match('\<LI\>\<A HREF=\"(.*)\"\>(.*)\<\/A\>', line).groups()
                    aTestCase[key]['url'].append(f"{matches[2]}|{matches[1]}")


################################################################################
# Name - getIndexPFSCounts
# Description - parses index.html filling in PFS counts and overall
################################################################################
def getIndexPFSCounts(host, path): # completed
    if getTestFramework(host, path) == 'pygash':
        return getIndexPFSCountsForPygash(host, path)
    ret = {}
    ret['num_pass'] = 0
    ret['num_fail'] = 0
    ret['num_skip'] = 0
    ret['num_no_result'] = "?"
    ret['status'] = "n/a"
    file = "masterlog.html"
    file2 = "index.html"
    fileName = f"/{host}{path}{file}"
    fileName2 = f"/{host}{path}{file2}"
    if (os.path.exists(fileName)):
        with open(fileName2) as handle: 
            for line in handle:
                line = line.strip()
                if line == "":
                    continue
                # TBD - this doesn't work
                # getting the overall status of the regression job
                if re.search('Overall Regression Status: (.*)\<', line):
                    matches = re.search('Overall Regression Status: (.*)\<',line).groups()
                    ret['status'] = matches[1]
                
                # getting the PFS counts
                if re.search('^\<LI\>\<B\>\<FONT COLOR=\"green\"\>PASSED\<\/FONT\>\<\/B\>: ([0-9]*)\<', line):
                    matches = re.search('^\<LI\>\<B\>\<FONT COLOR=\"green\"\>PASSED\<\/FONT\>\<\/B\>: ([0-9]*)\<', line).groups()
                    ret['num_pass'] = matches[1]
                
                if re.match('^\<LI\>\<B\>\<FONT COLOR=\"red\"\>FAILED\<\/FONT\>\<\/B\>: ([0-9]*)\<', line):
                    matches = re.match('^\<LI\>\<B\>\<FONT COLOR=\"red\"\>FAILED\<\/FONT\>\<\/B\>: ([0-9]*)\<', line).groups()
                    ret['num_fail'] = matches[1]
                
                if re.match('^\<LI\>\<B\>\<FONT COLOR=\"black\"\>SKIPPED\<\/FONT\>\<\/B\>: ([0-9]*)\<', line):
                    matches = re.match('^\<LI\>\<B\>\<FONT COLOR=\"black\"\>SKIPPED\<\/FONT\>\<\/B\>: ([0-9]*)\<', line).groups()
                    ret['num_skip'] = matches[1]
                
                if re.match('^\<LI\>\<B\>\<FONT COLOR=\"orange\"\>NO RESULT\<\/FONT\>\<\/B\>: ([0-9]*)\<', line):
                    matches = re.match('^\<LI\>\<B\>\<FONT COLOR=\"orange\"\>NO RESULT\<\/FONT\>\<\/B\>: ([0-9]*)\<', line).groups()
                    ret['num_no_result'] = matches[1]
                    return ret
    return ret

################################################################################
# Name - getIndexPFSCountsForPygash
# Description - parses summary.json filling in PFS counts and overall
################################################################################

def getIndexPFSCountsForPygash(host, path): #completed
    ret = {}
    ret['num_pass'] = 0
    ret['num_fail'] = 0
    ret['num_skip'] = 0
    ret['num_no_result'] = "0"
    ret['status'] = "n/a"
    getRunInfoForPygash(host, path)
    for testnum,testarray in aTestCase.items():
        for testparam,testvalue in testarray.items():
              if testparam == "result":
                 if testvalue == "PASSED":
                      ret['num_pass'] += 1
                 
                 if testvalue == "FAILED":
                      ret['num_fail'] += 1
                 
                 if testvalue == "SKIPPED":
                      ret['num_skip'] += 1
         
    if ret['num_fail'] > 0:
        ret['status'] = "FAIL"
    
    if ret['num_fail'] == 0 and ret['num_pass'] > 0:
        ret['status'] = "PASS"
    
    return ret

##################################################################################################
# NAME - getFirstTest
# DESCRIPTION - temporary function returning the first test key matching testName
# parameters - $testName
# note - this will go away once we can read the actual matching index from index.html
##################################################################################################
def getFirstTest(testName): #completed
    global aTestCase
    for key in aTestCase.keys():
        if aTestCase[key]['name'] == testName:
            return key
    
    return 0

##################################################################################################
# NAME - getSuiteTotal
# DESCRIPTION - just adds up the suite times for a total for each
# parameters - $action is either "est" or "act"
##################################################################################################
def getSuiteTotal(action):  #completed
    ret = 0
    for key in aTestCase.keys():
        try:    
            aTestSuite[key][action]
            ret += aTestSuite[key][action]
        except:
            pass
    return ret

##################################################################################################
# NAME - getPFSCounts
# DESCRIPTION - adds up the pass, fail, skip and total test counts
##################################################################################################
def getPFSCounts(aTestCase):
    ret = {}
    ret['num_pass'] = 0
    ret['num_fail'] = 0
    ret['num_skip'] = 0
    ret['num_executed'] = 0
    ret['num_unknown'] = 0
    ret['num_no_result'] = 0
    if aTestCase:
        for key in aTestCase.keys():
            if 'result' in aTestCase[key]:
                result = aTestCase[key]['result']
                if result == "PASSED":
                    ret['num_pass']+=1
                    ret['num_executed']+=1
                elif result == "FAILED":
                    ret['num_fail']+=1
                    ret['num_executed']+=1
                elif result == "SKIPPED":
                    ret['num_skip']+=1
                    ret['num_executed']+=1
                else:
                    ret['num_unknown']+=1
            else:
                ret['num_no_result']+=1
    return ret


##################################################################################################
# NAME - getPFSSubCounts
# DESCRIPTION - adds up the sub pass, fail, skip and total test counts
##################################################################################################
def getPFSSubCounts(): # completed

    global aSubTest
    ret = {}
    ret['num_pass'] = 0
    ret['num_fail'] = 0
    ret['num_skip'] = 0
    ret['num_executed'] = 0
    ret['num_unknown'] = 0
    ret['num_no_result'] = 0
    for key in aSubTest.keys():
        try:
            aTestSuite[key]['result']
            if aSubTest[key]['result'] == "PASSED":
                ret['num_pass'] += 1
                ret['num_executed'] += 1
            elif (aSubTest[key]['result'] == "FAILED"): 
                ret['num_fail'] += 1
                ret['num_executed'] += 1
            elif (aSubTest[key]['result'] == "SKIPPED"):
                ret['num_skip'] += 1
                ret['num_executed'] += 1
            else:
                ret['num_unknown'] += 1
                
        except:
            ret['num_no_result'] += 1
           
    return ret

##################################################################################################
# NAME - getPFSSuiteCounts
# DESCRIPTION - adds up the sub pass, fail, skip and total test counts
##################################################################################################
def getPFSSuiteCounts(): #completed
    global aTestSuite
    ret = {}
    ret['num_pass'] = 0
    ret['num_fail'] = 0
    ret['num_skip'] = 0
    ret['num_executed'] = 0
    ret['num_unknown'] = 0
    ret['num_no_result'] = 0
    for key in aTestSuite.keys():
        if aTestSuite[key].get('result') is not None:
            if aTestSuite[key]['result'] == "PASSED":
                ret['num_pass']+=1
                ret['num_executed']+=1
            elif aTestSuite[key]['result'] == "FAILED":
                ret['num_fail']+=1
                ret['num_executed']+=1
            elif aTestSuite[key]['result'] == "SKIPPED":
                ret['num_skip']+=1
                ret['num_executed']+=1
            else:
                ret['num_unknown']+=1
        else:
            ret['num_no_result']+=1
    return ret


###########################################################################
# NAME - getTimingInfo
# DESCRIPTION - get current running time params
# RETURNS - a structure with the following
# ret['suite_time_remaining'] - total job time remaining
# ret['running_test_name'] - the name of the running test
# ret['current_suite_name'] - the name of the running suite
# ret['current_suite_id'] - the id of the running suite
# ret['tests_remaining'] - number of tests remaining if in deferr mode
# ret['running_test_time_remaining'] - time left in the running_test_name
#                                      if negative, implies overtime
# ret['running_test_running_time'] - total time the running test has been running
# ret['comment'] - additional information if any
# ret['running_subtest_name'] - if known
# Oct 09 - ssteg - added deferr timing and re factored
# NOTE - must call getRunInfo first
###########################################################################
def getTimingInfo(deferrData, aTestSuite, aTestCase): #completed
    ret = {}
    if currentTestId is None:
        ret['comment'] = "Cannot determine test run time."
        return ret
     
    ret['current_suite_name'] = aTestSuite[aTestCase[currentTestId]['suite']]['name']
    ret['current_suite_id'] = aTestCase[currentTestId]['suite']
    ret['running_test_name'] = aTestCase[currentTestId]['name']
    ret['current_test_id'] = currentTestId
    ret['tests_remaining'] = 0
    ret['running_subtest_name'] = currentSubTestName
    lastTime = getLastEndTime(aTestCase, aTestSuite)
    timeNow = time.time()
    if lastTime == 0:
        lastTime = timeNow
    
    ret['running_test_running_time'] = timeNow - lastTime
    addedTime = 0
    if "unknown" in aTestCase[currentTestId]['est']:
        ret['running_test_time_remaining'] = aTestCase[currentTestId]['est'] - (timeNow - lastTime)
        if ret['running_test_time_remaining'] < 0:
            ret['comment'] = "is Exceeding Prediction by"
        else:
            addedTime = ret['running_test_time_remaining']
        
    else:
        ret['comment'] = "unknown duration, has been running for"
        ret['running_test_time_remaining'] = lastTime - timeNow
    
    if deferrData['type'] == "test" and not deferrData['name']:
        ret['suite_time_remaining'] = addedTime
        return ret
    
    stopSuite = -1
    if deferrData['type'] == "suite":
        stopSuite = aTestCase[currentTestId]['suite'] + 1
    
    stopTest = -1
    if deferrData['type'] == "test" and deferrData['name']:
        name = deferrData['name']
        for key3 in aTestCase:
            if aTestCase[key3]['name'] == name:
                stopTest = key3
                break
            
        
    
    ret['suite_time_remaining'] = 0
    for key2 in aTestCase.keys():
        if stopSuite == aTestCase[key2]['suite']:
            break
        
        if key2 == currentTestId and key2 == stopTest:
            break
        
        if key2 <= currentTestId:
            continue
        
        ret['tests_remaining']+=1
        ret['suite_time_remaining'] += aTestCase[key2]['est']
        #if ($stopTest == $key2) {
        #    break;
        #}
    
    ret['suite_time_remaining'] += addedTime
    return ret

###############################################################################
# Name - getLastEndTime
# Description - the last valid timestamp is either the starttime of the last
#               suite, or the last endtime of the last test in the completed,
#               whichever is greater
###############################################################################
def getLastEndTime(aTestCase, aTestSuite): #completed
    ret = 0
    for key in aTestCase.keys():
        if 'endtime' in aTestCase[key]:
            ret = aTestCase[key]['endtime']
    for key2 in aTestSuite.keys():
        if 'starttime' in aTestSuite[key2]:
            if aTestSuite[key2]['starttime'] > ret:
                ret = aTestSuite[key2]['starttime']
    return ret

###############################################################################
# Name - findTestIndex
# Description - find the first instance of testName at or after $current key.
#               Used to sync up when tests don't follow in sequence.
###############################################################################
def findTestIndex(testName, current): #completed
    for temp in aTestCase:
        key = temp[0]
        if key >= current:
            if aTestCase[key]['name'] == testName:
                return key
    return False

###############################################################################
# Name - didSomethingRun
# Description - didSomething Run in this $suite or not
###############################################################################
def didSomethingRun(suite): # completed
    for temp in aTestCase:
        key = temp [0]
        if aTestCase[key]['suite'] == suite:
            try:
                aTestCase[key]['result']
                return True
            except:
                continue
    return False

###############################################################################
# Name - isRunning
# Description - is this $job running now or not
###############################################################################
def isJobRunning(host,job): #completed
    inprogress = False
    arr = urlparse(job)
    job_name = arr.path
    ip_filepath = f"/{host}/jobs/inprogress"
    if os.path.exists(ip_filepath):
        with open(ip_filepath) as f:
            for line in f:
                if re.match('Follow the results at(\s+): (.*)',line):
                    job_inprogress = re.match('Follow the results at(\s+): (.*)',line).groups()[1]
                    job_inprogress = job_inprogress.strip('\r')
                    arr2 = urlparse(job_inprogress)
                    job_inprogress_name = arr2.path
                    if job_name == job_inprogress_name:
                        inprogress = True
    return inprogress

###############################################################################
# Name - getTestFramework
#
# Description - parse regression_framework and return its first line.  If
# the file does not exist, return 'gash'.  This file is used to know which test
# framework is used for the current regression (either gash or pygash)
###############################################################################
def getTestFramework (host, path): #completed
    framework = 'gash'
    framework_file = f"/{host}{path}regression_framework"
    with open(framework_file) as f:
        for line in f:
            framework = line
            break
    return framework.lower()

