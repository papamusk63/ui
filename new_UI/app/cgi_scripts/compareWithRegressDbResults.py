#!/usr/global/bin/python2.7

DEBUG = 0

import os, string, traceback
from threading import *
##import synchronize

keys = os.environ.keys()
from re import search
for key in keys:
   if not search("PYTHON_EGG_CACHE", key):
      os.environ["PYTHON_EGG_CACHE"]="/var/tmp/"


import sys
import re
import _mysql

## TODO's
# The IN operator does not work when you only have 1 testcase (skipSanity and runTest together)

class ParallelException(Exception):
    pass

def parallel(listOfFunctionArgumentTuples):
    """Runs each function in listOfFunctionArgumentTuples in parallel with its respective arguments.
       Answers list of return codes as returned by each function
       When any of the functions throws an exception, parallel will throw a ParallelException containing the stack trace
       from the original exception. When more functions raise exceptions, all stack traces are wrapped.
       Answer list of return values for each function

       listOfFunctionArgumentTuples (list of tuples):
            Each tuple looks like: (function, arglist) or (function, arglist, keyword arg list)
    """

    def runThread(resultList, exceptionList, counter, function, args, keywordArgs):
        try:
            result = apply(function, args, keywordArgs)
            #append a tuple with a counter and the result.
            resultList.append((counter, result))
        except Exception, ex:
            exceptionList.append(string.join(['Thread %s in utilities.parallel raised exception:\n' % counter]+traceback.format_exception(ex.__class__.__name__, ex.__str__(), sys.exc_traceback)))
    lstOfThreads = []
    resultList = []
    exceptionList = []
    counter = 0
    for functionTuple in listOfFunctionArgumentTuples:
        try:
            keywordArgs = functionTuple[2]
        except:
            keywordArgs = {}
        thread = Thread(target = runThread, args = (resultList, exceptionList, counter, functionTuple[0], functionTuple[1], keywordArgs))
        thread.start()
        lstOfThreads.append(thread)
        counter += 1
    for thread in lstOfThreads:
        thread.join()
    #check for exceptions
    if exceptionList:
        raise ParallelException(string.join(exceptionList, "\n-------------------------------------------\n"))
    resultList.sort()
    return map((lambda x: x[1]), resultList)

def usage(args):
    output = 'Please specify one argument only. Example %s /anrtb5/results/2010/Month_05/May_21/01:16:05.ipd-regress' % args[0]
    print output
    exit(1)

class CompareDbResult:
    def __init__(self, testName, testResult, buildItRanOn, tasId):
        self.testName = testName
        self.testResult = testResult
        self.buildItRanOn = buildItRanOn
        self.testAndSuiteId = tasId

    def __repr__(self):
        return "(%s, %s, %s, %s)" % (self.testName, self.testResult, self.buildItRanOn, self.testAndSuiteId)

    def getTestName(self):
        return self.testName

    def getBuild(self):
        return self.buildItRanOn

    def getResult(self):
        return self.testResult

    def getTestAndSuiteId(self):
        return self.testAndSuiteId


class CompareResult:
   def __init__(self):
      self.db = _mysql.connect("138.203.16.150","readOnlyUser", "onlyForReading", 'regressiondb')
      
   def fetchReleaseNumber(self, resultsDir):
       versionFile = open('%s/version.txt' % resultsDir, 'r')
       versionFileContents = versionFile.readline()
       versionFile.close()
       matched = re.match('(\d+\.\d)\.([FPIVXBS])', versionFileContents)
       if matched:
           return '%s %s' % (matched.group(1), matched.group(2))
       else:
           #private build
           matched = re.match('(\d\.\d)', versionFileContents)
           return '%s %s' % (matched.group(1), 'p')

   def fetchFailedTestsFromMail(self, resultsDir):
       emailFile = open('%s/email.txt' % resultsDir, 'r')
       emailText = emailFile.readlines()
       emailFile.close()
       failedTestsFromEmail = []
       doCopy=0
       for line in emailText:
          m=re.match('[^A]*FAILED TESTS.*', line)
          if m:
              doCopy=1
          isTestCase=1
          m=re.match('-------',line)
          if m:
              isTestCase=0
          m=re.match('FAILED TESTS',line)
          if m:
              isTestCase=0
          if line.strip(' ') == "":
              isTestCase=0
          if doCopy and isTestCase:
              tc=line.strip(" \n\r")
              tc=tc.replace('::','_')
              failedTestsFromEmail.append(tc)
       return failedTestsFromEmail

   def fetchTestInformation(self, resultsDir):
       self.failedTestsFromEmail = self.fetchFailedTestsFromMail(resultsDir)
       testNamesResultList = []
       testFile = open('%s/masterlog.txt' % resultsDir, 'r')
       testFileContents = testFile.readlines()
       testFile.close()
       testlist = [aLine.strip() for aLine in testFileContents if aLine.startswith('RESULT')  or aLine.find('END ::TestDB::TestSuiteCleanup') != -1]
       for testResultLine in testlist:
           testResultTuple = self._handleTestcaseResultLine(testResultLine)
           if not testResultTuple:
               testResultTuple = self._handleCleanupResultLine(testResultLine)
           if testResultTuple:
               testNamesResultList.append(testResultTuple)
       return testNamesResultList

   def _handleTestcaseResultLine(self, testResult):
       outputList = testResult.strip().split(' ')
       try:
           indexOfTestcase = outputList.index('case')
       except ValueError:
           try:
               indexOfTestcase = outputList.index('Case')
           except ValueError:
               try:
                   indexOfTestcase = outputList.index('Test')
               except ValueError:
                   return None
       indexOfTestcase += 1
       testName = outputList[indexOfTestcase]
       testResult = outputList[1].strip(' :')
       if testName in self.failedTestsFromEmail:
           testResult = 'FAILED'
       if testName:
           return (testName, testResult)
       return None

   def _handleCleanupResultLine(self, testResult):
       """Looks like 'MASTER: END ::TestDB::TestSuiteCleanup::VrrpV3'"""
       m=re.match('.*::(TestSuiteCleanup.*)', testResult)
       if m:
           cleanupSuite = m.group(1)
           cleanupSuite = cleanupSuite.replace("::", "_")
           result = 'PASSED' # only failed if it is found in the email section of Failed tests
           if cleanupSuite in self.failedTestsFromEmail:
               result = 'FAILED'
       return (cleanupSuite, result)

   def fetchProduct(self, resultsDir):
       product = '7750'
       argsFile = open('%s/args' % resultsDir, 'r')
       argsFileContent = argsFile.readline()
       argsFile.close()
       if argsFileContent.find('7450') != -1:
           product = '7450'
       elif argsFileContent.find('7710') != -1:
           product = '7710'
       elif argsFileContent.find('7950') != -1:
           product = '7950'
       return product

   def fetchInfoFromResult(self, resultsDir):
       releaseNr = self.fetchReleaseNumber(resultsDir)
       testResultList = self.fetchTestInformation(resultsDir)
       product = self.fetchProduct(resultsDir)
       return releaseNr, testResultList, product

   def _getBranchFromBuild(self, release):
       completeBranch = "TiMOS_0_0"
       build, branchIndication = release.split(' ')
       build = build.replace('.', '_')
       if build == '0_0':
           return "TiMOS_0_0"
       else:
           completeBranch = "TiMOS_%s" % build
           if branchIndication == 'B':
               completeBranch += '_B1'
           elif branchIndication == 'S':
               completeBranch += '_current'
           elif branchIndication == 'P':
               completeBranch += '_current'
           elif branchIndication == 'I':
               completeBranch += ''
           elif branchIndication == 'F':
               completeBranch += '_future'
           elif branchIndication == 'V':
               completeBranch += '_future'
           elif branchIndication == 'X':
               completeBranch += '_future'
           elif branchIndication == 'p':
               completeBranch += '_current'
           return completeBranch

   def _getbranchIdFromBranchName(self, branchName):
       query = "SELECT id FROM branch WHERE name='%s'" % branchName
       res = self._executeQuery(query)
       resultRow = res.fetch_row(how=2)
       return resultRow[0]['branch.id']

   def _getSqlConstraint(self, testList):
       constraint = ''
       for test in testList:
           constraint += "testAndSuite_name.name='%s' or " % test
       return constraint[:-3]

   def _getSqlQuery(self, release, testList, product):
       self.branchName = self._getBranchFromBuild(release)
       self.branchId = self._getbranchIdFromBranchName(self.branchName)

       query = """SELECT testAndSuite_name.name, testAndSuite.tas_status_id_Pass, testAndSuite.tas_status_id_Fail, testAndSuite.id
           FROM testAndSuite_name join testAndSuite on testAndSuite.tas_name_id = testAndSuite_name.id
              JOIN testAndSuite_status on testAndSuite.id = testAndSuite_status.testAndSuite_id

           WHERE testAndSuite.branch_id = '%(branch_id)s'
           AND testAndSuite_status.platform IN ('7xxx', '%(platform)s')
           AND (%(testcasesConstraint)s) ;
    """ % { 'branch_id' : self.branchId, 'testcasesConstraint' : self._getSqlConstraint(testList), 'platform':product }
       return query

   def _executeQuery(self, queryToExecute):
       #print queryToExecute
       self.db.query(queryToExecute)
       res=self.db.store_result()
       return res

   def closeDbConnection(self):
       self.db.close()

   def parseResult(self, queryResult):
       resultDict = {}
       row=queryResult.fetch_row(how=2)
       while row:
           newResult = self.parseOneResultRow(row[0])
           testName = newResult.getTestName()
           result = (newResult.getResult(), newResult.getBuild(), newResult.getTestAndSuiteId())
           resultDict[testName] = result
           row=queryResult.fetch_row(how=2) # fetch Next row from the result
       return resultDict

   def getLastTestResult(self, passBuild, failBuild):
       if passBuild == '':
           if failBuild != '':
               return 'FAILED'
           return 'GHOST'

       if failBuild == '':
           return 'PASSED'

       if passBuild.find('-') != -1:
           passNr = int(passBuild[passBuild.find('-')+1:])
       else:
           passNr = int(passBuild[1:])

       if failBuild.find('-') != -1:
           failNr = int(failBuild[failBuild.find('-')+1:])
       else:
           failNr = int(failBuild[1:])

       if passNr >= failNr:
           return 'PASSED'
       else:
           return 'FAILED'

   def parseOneResultRow(self, resultDict):
      lastPass = ''
      lastFail = ''
      if resultDict['testAndSuite.tas_status_id_Pass'] != '0':
         # Test passed: Overall result of the regressRun can be passed or failed
         q_pass = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Pass
where testAndSuite_status.id = '%s';""" % resultDict['testAndSuite.tas_status_id_Pass']

         # Test passed: Overall result of the regressRun can be passed or failed
         q_pass2 = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Fail
where testAndSuite_status.id = '%s';""" % resultDict['testAndSuite.tas_status_id_Pass']

         res = self._executeQuery(q_pass)
         passPass = res.fetch_row(how=2)
         if len(passPass) != 0:
            lastPass = passPass[0]['regressRun.version']
         else:
            res = self._executeQuery(q_pass2)
            passFail = res.fetch_row(how=2)
            lastPass = passFail[0]['regressRun.version']
         
      if resultDict['testAndSuite.tas_status_id_Fail'] != '0':
         # Test failed: Overall result of the regressRun can only be Failed
         q_fail = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Fail
where testAndSuite_status.id = '%s';""" % resultDict['testAndSuite.tas_status_id_Fail']
         res = self._executeQuery(q_fail)
         failId = res.fetch_row(how=2)
         if len(failId) != 0:
            lastFail = failId[0]['regressRun.version']
      testName = resultDict['testAndSuite_name.name']
      lastTestResult = self.getLastTestResult(lastPass, lastFail)
       
      if lastTestResult == 'PASSED':
          latestRunBuild = lastPass
      else:
          latestRunBuild = lastFail
      return CompareDbResult(testName, lastTestResult, latestRunBuild, resultDict['testAndSuite.id'])

   def fetchInfoFromDb(self, release, testList, product):
      query = self._getSqlQuery(release, testList, product)
      result = self._executeQuery(query)
      parsedResult = self.parseResult(result)
      return parsedResult

   def printHtmlTable(self, testResultList, dbInfoDict):
      print '<table border="1">'
      print '<th>Result from your run</th>'
      print '<th>Result form RegressDb</th>'
      for testName, testResult in testResultList:
         print '<tr>'
         fontcolor = 'black'
         if testResult == 'FAILED':
             fontcolor = 'red'
         font2 = fontcolor #only change if dbResult=FAILED and tesResult=PASSED
         if testName in dbInfoDict.keys():
            dbResult = dbInfoDict[testName][0]
            if dbResult != testResult:
               bgcolor = 'yellow'
               if testResult == 'PASSED':
                  bgcolor = 'lightgreen'
                  font2 = 'red'
               elif testResult == 'FAILED':
                  bgcolor = 'red'
                  if fontcolor == 'red':
                     fontcolor = 'black'
                     font2 = 'black'
               print '<td bgcolor="%s"><font color="%s"> <a href="http://138.203.16.150/regression/index_ng.php?cmd=testCaseMan&branch_id=%s&tasId=%s&branch=%s&testCase=%s">%s</a> %s </font> </td>' % (bgcolor, fontcolor, self.branchId, dbInfoDict[testName][2], self.branchName, testName, testName, testResult)
               print '<td> <font color="%s"> %s %s </font> </td>' % ( font2, dbInfoDict[testName][0], dbInfoDict[testName][1] )
            else:
               print '<td>  <font color="%s">  <a href="http://138.203.16.150/regression/index_ng.php?cmd=testCaseMan&branch_id=%s&tasId=%s&branch=%s&testCase=%s">%s</a> %s </font> </td>' % (fontcolor, self.branchId, dbInfoDict[testName][2], self.branchName, testName, testName, testResult)
               print '<td> <font color="%s"> %s %s </font> </td>' % ( font2, dbInfoDict[testName][0], dbInfoDict[testName][1] )
         else:
             print '<td><font color="%s"> %s %s </font></td>' % (fontcolor, testName, testResult)
             print '<td> %s %s </td>' % ('No Info', 'in regressDb')
         print '</tr>'
      print '</table>'


class FailingSinceDbResult:
   def __init__(self, testName, allFailedVersions, lastPassedVersion, actionReasonTuple):
      self.testName = testName
      self.allFailedVersions = [each for each in allFailedVersions if each]
      self.lastPassedVersion = lastPassedVersion
      self.actionReasonTuple = actionReasonTuple

   def __repr__(self):
      return "(%s, %s, %s)" % (self.testName, self.allFailedVersions, self.lastPassedVersion, self.actionReasonTuple)

   def getTestName(self):
      return self.testName

   def getRemarks(self):
      return self.actionReasonTuple

   def getBuildsItFailedOn(self):
      return self.allFailedVersions

   def getLastPassedVersion(self):
      return self.lastPassedVersion

   def getFailingSince(self):
      def reverseSortBuildNumbers(firstBuild, secondBuild):
         fi = int(re.match('[APIBRSV]([0-9]\-)?([0-9]*)', firstBuild).group(2))
         si = int(re.match('[APIBRSV]([0-9]\-)?([0-9]*)', secondBuild).group(2))
         if fi < si:
             return 1
         elif fi > si:
             return -1
         else:
             return 0

      self.allFailedVersions.sort(reverseSortBuildNumbers)
      return self.allFailedVersions


class FailingSinceComparator(CompareResult):
   def _executeQuery(self, queryToExecute):
       #print queryToExecute
       db = _mysql.connect("138.203.16.150","readOnlyUser", "onlyForReading", 'regressiondb')
       db.query(queryToExecute)
       res=db.store_result()
       return res

   def fetchInfoFromTestAndSuite(self, release, testList, product):
      self.branchName = self._getBranchFromBuild(release)
      self.branchId =  self._getbranchIdFromBranchName(self.branchName)
      query = """SELECT testAndSuite_name.name as name, testAndSuite.id as id, testAndSuite.tas_status_id_Pass as Pass_id, testAndSuite.tas_status_id_Fail as Fail_id, testAndSuite.tas_history_id as History_id
           FROM testAndSuite join testAndSuite_name ON testAndSuite.tas_name_id = testAndSuite_name.id
           JOIN testAndSuite_status on testAndSuite.id = testAndSuite_status.testAndSuite_id
           WHERE testAndSuite.branch_id = '%(branch_id)s'
           AND testAndSuite_status.platform IN ('7xxx', '%(platform)s')
           AND (%(testcasesConstraint)s);
""" % { 'branch_id' : self.branchId, 'testcasesConstraint' : self._getSqlConstraint(testList), 'platform':product }
      result = self._executeQuery(query)
      passAndFailDict = {}
      row = result.fetch_row(how=1)
      while row:
         row = row[0]
         passAndFailDict[row['id']] = row
         row = result.fetch_row(how=1)
      return passAndFailDict

   def fetchInfoFromRunTable(self, id):
      newInfoDict = {}
      query = """SELECT SubRes.tas_id as id, GROUP_CONCAT(SubRes.rr_id) as rrIds
FROM (SELECT run.testAndSuite_id AS tas_id, run.regressRun_id AS rr_id
FROM run 
WHERE run.testAndSuite_id = %(testcaseId)s
AND run.status = 'FAILED'
ORDER BY run.regressRun_id DESC LIMIT 10) AS SubRes
GROUP BY SubRes.tas_id;
""" % { 'testcaseId' : id }
      result = self._executeQuery(query)
      row = result.fetch_row(how=1)
      addedId = 0
      while row:
         row = row[0]
         newInfoDict[row['id']] = row
         row = result.fetch_row(how=1)
         addedId = 1

      if not addedId:
         newInfoDict[id] = {'id':id, 'rrIds':None}
      return newInfoDict

   def fetchInfoFromHistoryTable(self, historyIdList):
      newInfoDict = {}
      idTuple = tuple(historyIdList)
      if len(historyIdList) > 1:
          historyIdTest = "IN  %(testcaseIds)s"  % { 'testcaseIds' : idTuple }
      else:
          historyIdTest = "=  %(testcaseId)s" % { 'testcaseId' : idTuple[0] }
      query = """SELECT testAndSuite_history.testAndSuite_id AS id, testAndSuite_history.action AS action, testAndSuite_history.reason AS reason
FROM testAndSuite_history 
WHERE 
testAndSuite_history.id %(historyIdTest)s 
;
""" % { 'historyIdTest' : historyIdTest }
      result = self._executeQuery(query)
      row = result.fetch_row(how=1)
      while row:
         row = row[0]
         newInfoDict[row['id']] = row
         row = result.fetch_row(how=1)
      return newInfoDict      

   def gatherResult(self, testAndSuiteDict, runDict, historyDict):
      resultDict = {}
      for anId in testAndSuiteDict.keys():
         testName, lastTestResult, latestRunBuild = self.fetchVersion(testAndSuiteDict[anId])
         allFailedVersions = self.fetchFailingSinceVersions(testAndSuiteDict[anId], runDict[anId])
         lastPassedVersion = self.fetchLastPassedVersion(testAndSuiteDict[anId])
         actionReason = self.fetchActionReasonFields(historyDict[anId])
         result = (lastTestResult, latestRunBuild, anId, allFailedVersions, lastPassedVersion, actionReason)
         resultDict[testName] = result
      return resultDict

   def getLastTestResult(self, passBuild, failBuild):
       if passBuild == '':
           if failBuild != '':
               return 'FAILED'
           return 'GHOST'

       if failBuild == '':
           return 'PASSED'

       if passBuild.find('-') != -1:
           passNr = int(passBuild[passBuild.find('-')+1:])
       else:
           passNr = int(passBuild[1:])

       if failBuild.find('-') != -1:
           failNr = int(failBuild[failBuild.find('-')+1:])
       else:
           failNr = int(failBuild[1:])

       if passNr >= failNr:
           return 'PASSED'
       else:
           return 'FAILED'

   def fetchVersion(self, testAndSuiteDictPerTestcase):
      lastPass = ''
      lastFail = ''
      if testAndSuiteDictPerTestcase['Pass_id'] != '0':
         # Test passed: Overall result of the regressRun can be passed or failed
         q_pass = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Pass
where testAndSuite_status.id = '%s';""" % testAndSuiteDictPerTestcase['Pass_id']

         # Test passed: Overall result of the regressRun can be passed or failed
         q_pass2 = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Fail
where testAndSuite_status.id = '%s';""" % testAndSuiteDictPerTestcase['Pass_id']

         res = self._executeQuery(q_pass)
         passPass = res.fetch_row(how=2)
         if len(passPass) != 0:
            lastPass = passPass[0]['regressRun.version']
         else:
            res = self._executeQuery(q_pass2)
            passFail = res.fetch_row(how=2)
            lastPass = passFail[0]['regressRun.version']
         
      if testAndSuiteDictPerTestcase['Fail_id'] != '0':
         # Test failed: Overall result of the regressRun can only be Failed
         q_fail = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Fail
where testAndSuite_status.id = '%s';""" % testAndSuiteDictPerTestcase['Fail_id']
         res = self._executeQuery(q_fail)
         failId = res.fetch_row(how=2)
         if len(failId) != 0:
            lastFail = failId[0]['regressRun.version']
      testName = testAndSuiteDictPerTestcase['name']
      lastTestResult = self.getLastTestResult(lastPass, lastFail)
       
      if lastTestResult == 'PASSED':
          latestRunBuild = lastPass
      else:
          latestRunBuild = lastFail
      return (testName, lastTestResult, latestRunBuild)

   def fetchFailingSinceVersions(self, testAndSuiteDictPerTestcase, runDictPerTestcase):
      def reverseSortBuildNumbers(firstBuild, secondBuild):
         fi = int(re.match('[APIBRSV]([0-9]\-)?([0-9]*)', firstBuild).group(2))
         si = int(re.match('[APIBRSV]([0-9]\-)?([0-9]*)', secondBuild).group(2))
         if fi < si:
             return 1
         elif fi > si:
             return -1
         else:
             return 0
      ## Get the last versions on which the test failed
      allFailedVersions = []
      if testAndSuiteDictPerTestcase['Fail_id'] != '0':
         # Test failed: Overall result of the regressRun can only be Failed, or test can be skipped so nu run exists for this test!
         if runDictPerTestcase['rrIds']:
            allRegressrunIds = runDictPerTestcase['rrIds']
            if allRegressrunIds.find(',') != -1:
               allRegressrunIds = allRegressrunIds[:allRegressrunIds.rindex(',')] # remove the last entry, since that may be cut by group_concat_max_len
            q_fail = """select regressRun.version from regressRun 
   where regressRun.id in (%s);""" % allRegressrunIds

            res = self._executeQuery(q_fail)
            failId = res.fetch_row(how=2)
            while len(failId) != 0:
               allFailedVersions.append(failId[0]['regressRun.version'])
               failId = res.fetch_row(how=2)
         else:
            # Test was skipped but never really failed (entry in tas_status_id_Fail but not in regressRun)
            allFailedVersions = ["Last failure too old!"]

      allFailedVersions.sort(reverseSortBuildNumbers)
      return allFailedVersions

   def fetchLastPassedVersion(self, testAndSuiteDictPerTestcase):
      ## Get the last version on which the test passes
      lastPassedVersion = None
      if testAndSuiteDictPerTestcase['Pass_id'] != '0':
         # Test passed, but overall regressRun might have been failed
         q_pass = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Pass
where testAndSuite_status.id = '%s';""" % testAndSuiteDictPerTestcase['Pass_id']

         # Test passed: Overall result of the regressRun can be passed or failed
         q_pass2 = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Fail
where testAndSuite_status.id = '%s';""" % testAndSuiteDictPerTestcase['Pass_id']

         res = self._executeQuery(q_pass)
         passPass = res.fetch_row(how=2)
         if len(passPass) != 0:
            lastPassedVersion = passPass[0]['regressRun.version']
         else:
            res = self._executeQuery(q_pass2)
            passFail = res.fetch_row(how=2)
            lastPassedVersion = passFail[0]['regressRun.version']
         return lastPassedVersion

   def fetchActionReasonFields(self, historyDictPerTestcase):
      ## Get the action and reason fields
      action = ' '
      reason = ' '
      if historyDictPerTestcase.has_key('action'):
         a = historyDictPerTestcase['action']
         if a.strip(','):
            action = historyDictPerTestcase['action']
      if historyDictPerTestcase.has_key('reason'):
         r = historyDictPerTestcase['reason']
         if r.strip(','):
            reason = historyDictPerTestcase['reason']
      return (reason, action)

   def fetchInfoFromDb(self, releaseNr, testNamesList, product):
      # TODO: make this parallel!

      tmp1 = self.fetchInfoFromTestAndSuite(releaseNr, testNamesList, product)
      historyIds = [each['History_id'] for each in tmp1.values()]

      parrallelRunQueries = []
      allTestAndSuiteIds = tmp1.keys()
      nrOfIterations = len(allTestAndSuiteIds)
      index = 0
      while index < nrOfIterations:
          aTestAndSuiteId = allTestAndSuiteIds[index]
          newFunction = (self.fetchInfoFromRunTable, [aTestAndSuiteId])
          parrallelRunQueries.append(newFunction)
          index += 1

      listOfRunResults = parallel(parrallelRunQueries)
      tmp2 = {}
      for each in listOfRunResults:
          k = each.items()[0][0]
          v = each.items()[0][1]
          tmp2[k] = v

      tmp3 = self.fetchInfoFromHistoryTable(historyIds)

      dbInfoDictWithAtLeastOneFailingResult = self.gatherResult(tmp1, tmp2, tmp3)
      alreadyHandledTestcases = dbInfoDictWithAtLeastOneFailingResult.keys()
      reducedTestList = [each for each in testNamesList if each not in alreadyHandledTestcases]
      dbInfoDictWithAllPassingResult = {}
      # TODO: copy previous way of working!
      if reducedTestList:
         query = self._getSqlQueryForAllPasses(releaseNr, reducedTestList, product)
         result = self._executeQuery(query)
         dbInfoDictWithAllPassingResult = self.parseResult(result)

      # merge both dictionaries
      for each in dbInfoDictWithAllPassingResult.keys():
         dbInfoDictWithAtLeastOneFailingResult[each] = dbInfoDictWithAllPassingResult[each]
         
      return dbInfoDictWithAtLeastOneFailingResult

   def _getSqlQueryForAllPasses(self, release, testList, product):
      branchName = self._getBranchFromBuild(release)
      # There is no failed run
      query = """SELECT testAndSuite_name.name, testAndSuite.tas_status_id_Pass, testAndSuite.tas_status_id_Fail
           FROM testAndSuite_name join testAndSuite on testAndSuite.tas_name_id = testAndSuite_name.id
              JOIN run on testAndSuite.id = run.testAndSuite_id
              JOIN testAndSuite_status on testAndSuite.id = testAndSuite_status.testAndSuite_id
           WHERE testAndSuite.branch_id = '%(branch_id)s'
           AND testAndSuite_status.platform IN ('7xxx', '%(platform)s')
           AND (%(testcasesConstraint)s)
           GROUP BY testAndSuite_name.name;
""" % { 'branch_id' : self._getbranchIdFromBranchName(branchName), 'testcasesConstraint' : self._getSqlConstraint(testList), 'platform':product }
      return query

   def parseResult(self, queryResult):
       resultDict = {}
       row=queryResult.fetch_row(how=2)
       while row:
           basicResult, failingSinceResult = self.parseOneResultRow(row[0])
           testName = basicResult.getTestName()
           result = (basicResult.getResult(), basicResult.getBuild(), basicResult.getTestAndSuiteId(), failingSinceResult.getFailingSince(), failingSinceResult.getLastPassedVersion(), failingSinceResult.getRemarks())
           resultDict[testName] = result
           row=queryResult.fetch_row(how=2) # fetch Next row from the result
       return resultDict

   def parseOneResultRow(self, resultDict):
      basicCompareDbResult = CompareResult.parseOneResultRow(self, resultDict)
      failingSinceDbResult = self.parseExtraFieldsResultRow(resultDict)
      return (basicCompareDbResult, failingSinceDbResult)

   def parseExtraFieldsResultRow(self, resultDict):
      ## 1. Get the last 10 versions on which the test failed
      allFailedVersions = []
      if resultDict['testAndSuite.tas_status_id_Fail'] != '0':
         # Test failed: Overall result of the regressRun can only be Failed, or test can be skipped so nu run exists for this test!
         if resultDict.has_key('rrIds'):
            allRegressrunIds = resultDict['rrIds']
            if allRegressrunIds.find(',') != -1:
               allRegressrunIds = allRegressrunIds[:allRegressrunIds.rindex(',')] # remove the last entry, since that may be cut by group_concat_max_len
            q_fail = """select regressRun.version from regressRun 
   where regressRun.id in (%s);""" % allRegressrunIds

            res = self._executeQuery(q_fail)
            failId = res.fetch_row(how=2)
            while len(failId) != 0:
               allFailedVersions.append(failId[0]['regressRun.version'])
               failId = res.fetch_row(how=2)
         else:
            # Test was skipped but never really failed (entry in tas_status_id_Fail but not in regressRun)
            allFailedVersions = ["Test skipped and never really failed!"]
            
      testName = resultDict['testAndSuite_name.name']

      ## 2. Get the last version on which the test passes
      lastPassedVersion = None
      if resultDict['testAndSuite.tas_status_id_Pass'] != '0':
         # Test passed, but overall regressRun might have been failed
         q_pass = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Pass
where testAndSuite_status.id = '%s';""" % resultDict['testAndSuite.tas_status_id_Pass']

         # Test passed: Overall result of the regressRun can be passed or failed
         q_pass2 = """select regressRun.version from regressRun join testAndSuite_status on regressRun.id = testAndSuite_status.regressRun_id_Fail
where testAndSuite_status.id = '%s';""" % resultDict['testAndSuite.tas_status_id_Pass']

         res = self._executeQuery(q_pass)
         passPass = res.fetch_row(how=2)
         if len(passPass) != 0:
            lastPassedVersion = passPass[0]['regressRun.version']
         else:
            res = self._executeQuery(q_pass2)
            passFail = res.fetch_row(how=2)
            lastPassedVersion = passFail[0]['regressRun.version']

      ## 3. Get the action and reason fields
      action = ' '
      reason = ' '
      if resultDict.has_key('testAndSuite_history.action'):
         a = resultDict['testAndSuite_history.action']
         if a.strip(','):
            action = resultDict['testAndSuite_history.action']
      if resultDict.has_key('testAndSuite_history.reason'):
         r = resultDict['testAndSuite_history.reason']
         if r.strip(','):
            reason = resultDict['testAndSuite_history.reason']

      return FailingSinceDbResult(testName, allFailedVersions, lastPassedVersion, (reason, action))

   def printHtmlTable(self, testResultList, dbInfoDict):
      print '<table border="1">'
      print '<th>Result from your run</th>'
      print '<th>Last result from RegressDb</th>'
      print '<th>Last 10 failing versions from RegressDb</th>'
      print '<th>Last passing version from RegressDb</th>'
      print '<th>Reason/Action</th>'
      for testName, testResult in testResultList:
         print '<tr>'
         fontcolor = 'black'
         if testResult == 'FAILED':
             fontcolor = 'red'
         font2 = fontcolor #only change if dbResult=FAILED and tesResult=PASSED
         if testName in dbInfoDict.keys():
            dbResult = dbInfoDict[testName][0]
            if dbResult != testResult:
               bgcolor = 'yellow'
               if testResult == 'PASSED':
                  bgcolor = 'lightgreen'
                  font2 = 'red'
               elif testResult == 'FAILED':
                  bgcolor = 'red'
                  if fontcolor == 'red':
                     fontcolor = 'black'
                     font2 = 'black'
               print '<td bgcolor="%s"><font color="%s"> <a href="http://138.203.16.150/regression/index_ng.php?cmd=testCaseMan&branch_id=%s&tasId=%s&branch=%s&testCase=%s">%s</a> %s </font></td>' % (bgcolor, fontcolor, self.branchId, dbInfoDict[testName][2], self.branchName, testName, testName, testResult)
               print '<td> <font color="%s"> %s %s </font> </td>' % (font2, dbInfoDict[testName][0], dbInfoDict[testName][1])
               print '<td> %s </td>' % (dbInfoDict[testName][3][:10])
               print '<td> %s </td>' % (dbInfoDict[testName][4])
               print '<td> %s %s </td>' % (dbInfoDict[testName][5])
            else:
               print '<td> <font color="%s"> <a href="http://138.203.16.150/regression/index_ng.php?cmd=testCaseMan&branch_id=%s&tasId=%s&branch=%s&testCase=%s">%s</a> %s </font></td>' % (fontcolor, self.branchId, dbInfoDict[testName][2], self.branchName, testName, testName, testResult)
               print '<td> <font color="%s"> %s %s </font> </td>' % (font2, dbInfoDict[testName][0], dbInfoDict[testName][1])
               print '<td> %s </td>' % (dbInfoDict[testName][3][:10])
               print '<td> %s </td>' % (dbInfoDict[testName][4])
               print '<td> %s %s </td>' % (dbInfoDict[testName][5])
         else:
             print '<td><font color="%s"> %s %s </font></td>' % (fontcolor, testName, testResult)
             print '<td> %s %s </td>' % ('No Info', 'in regressDb')
             print '<td> %s </td>' % ('No Info')
             print '<td> %s </td>' % ('No Info')
             print '<td> %s </td>' % (' ')
             
         print '</tr>'
      print '</table>'


if __name__ == '__main__':
   if len(sys.argv) != 2:
      usage(sys.argv)

   resultsDirectory = sys.argv[1]

   # PART 1 FAST!
   comp = CompareResult()
   releaseNr, testResultList, product = comp.fetchInfoFromResult(resultsDirectory)
   testNamesList = [testName for testName, testResult in testResultList]
   dbInfoDict = comp.fetchInfoFromDb(releaseNr, testNamesList, product)
   comp.printHtmlTable(testResultList, dbInfoDict)
   comp.closeDbConnection()

   # Print part 1 immediatly
   sys.stdout.flush()
   print "<b>More detailed results from RegressDb coming up: (in max 2 minutes)</b><br><br>"
   sys.stdout.flush()

   # PART 2 SLOWER (max 2 minutes)
   comp = FailingSinceComparator()
   releaseNr, testResultList, product = comp.fetchInfoFromResult(resultsDirectory)
   blacklist = ['TestSuiteCleanup_initial', 'TestSuiteCleanup_Sanity', 'TestSuiteCleanup_finished']
   testNamesList = [testName for testName, testResult in testResultList if ( (not testName.startswith('sanity_')) and (testName not in blacklist) )]
   dbInfoDict = comp.fetchInfoFromDb(releaseNr, testNamesList, product)
   comp.printHtmlTable(testResultList, dbInfoDict)
   comp.closeDbConnection() 
   sys.stdout.flush()



