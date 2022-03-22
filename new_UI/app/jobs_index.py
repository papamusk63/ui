from email import message
from ensurepip import version
from time_left import *
from common_func import get_files, array_map, get_content, strpos, file_put_contents
from read_masterlog2 import *
import os
import re

myhost = None
host = 'hostname -s'.strip()
rowserver = os.getenv('ROWSERVER')

aTb = FillTestbedArray("/usr/global/bin/regress.params")
host_ip = aTb[host]['IP']

jobs_files = {}
inprogress = {}
id = 0
jobs_path= "/host/jobs"
entry = "/host"
location = {}
jobid = {}
result_id = {}



def job_index(request):
    if host_ip:
        host_ip = ('hostname -f').strip()
    if rowserver:
        running_ip = os.system(f"/usr/global/bin/readTestbedParams {host} running_ip linux")
    else:
        running_ip = host_ip

    if rowserver == host:
        temp = request['SERVER_NAME']
        domain_not_wanted = {}
        domain_not_wanted['host'] = temp.split(".")


    get_files(jobs_path)
    
    # definition for the favicon, whatever that is
    print("<link rel=\"shortcut icon\" href=\"http://myhost/status/images/favicon.ico\">\n")

    
    # definition for the default style sheet
    print("<link rel=\"stylesheet\" type=\"text/css\" href=\"http://myhost/status/css/test.css\">\n")

    # definition for the overlib javascript (the pop up thing)
    print("<script language='Javascript' src='overlib.js'></script>\n")

    user = request["GUIAuth"]
    if user == "":
        user = "Unknown User"
    
    ps = "<form action=http://running_ip/status/cgi_scripts/make_note.cgi method=GET onsubmit=\'return check_note(this)\'><table border=1 width=500px><tr><input type=hidden name=host value=host><input type=hidden name=user value=user><input type=hidden name=host_ip value=myhost><td class=title_bar width=200>Post this: </td><td class=content_2><input type=text size=100 name=note></td></tr><tr><td class=content colspan=3><input type=submit value=OK></td></tr></table></form>";
    output = make_pop_up(ps)

    print("<tr><td class=content_2 align=center colspan=2><input type=submit output value='Create Bed Note'></td></tr>")


def make_pop_up(description):
    return "onclick=\"return overlib('description',TEXTFONTCLASS,'textFontClass',CAPTIONFONTCLASS,'capfontClass2',CLOSEFONTCLASS,'capfontclass2',CAPTION,'Details',STICKY);\" onclick=\"return nd();\""

'''
 * READ FILES IN THE GIVEN PATH
'''
def get_files(path):
    global jobs_files

    if path:
        fd = open(path)
        if fd:
            for part in fd:
                if part != "." and part != "..":
                    jobs_files["test"] = part
                elif re.search('/^\.(\S+)/', part) is None and re.search('/index\.(\S+)/', part) is None:
                    if part == 'inprogress':
                        jobs_files["inprogress"] = part
                    else:
                        jobs_files["general"] = part
    

'''
 * READ ARGUMENTS OF CURRENT RUNNING JOB
 * VERSION, ARGS, URL, PATH
'''
def get_inprogress_detail(ipg):
    global inprogress
    global location
    global jobid
    global result_id

    file = open(ipg, "r")
    if file is None:
        return "No jobrunning file found"

    matches = []
    for line in file:
        if re.search('/Version(.*): (\S+)/', line, matches):
            version = matches[2]
            inprogress["version"] = version
        elif re.search('/JobID(.*): (\S+)/', line, matches):
            jobid = matches[2]
            inprogress['jobid'] = jobid
        elif re.search('/Arguments(.*): (\S+)/', line, matches):
            args = matches[2]
        elif re.search('/Follow(.*): (\S+)/', line, matches):
            url = matches[2]
    

    location = "/parts[3]/parts[4]/parts[5]/parts[6]/"
    result_id = "parts[7]"
    get_content()


'''
 * READ DETAIL OF THE CURRENT RUNNING JOB
 * CURRENT_RUNNING, TIME_LEFT, TEST_LEFT
'''
def get_content():
    global myhost
    global host
    global location
    global id
    global current_test
    global current_suite
    global result_id
    global here_non_url
    global aTestCase
    global aTestSuite
    global systemBed

    here_url = f"http://{myhost}{location}{result_id}"
    img_loc = f"http://{myhost}status/result_index"
    here_non_url = f"/{host}{location}{result_id}"
    path = f"{location}{result_id}"

    version = get_file_content(f"{here_non_url}/version.txt")
    if version:
        version = "n/a"
    args = get_file_content(f"{here_non_url}/args")
    if args is not None:
        args = "n/a"
    
    # strip off the -idleBedStartingUp, could be anywhere
    aArgs = args.split(" ")
    newArgs = ""
    for inx, val in enumerate(aArgs):
        if aArgs[inx] != "-idleBedStartingUp":
            newArgs = newArgs + aArgs[inx]

    args = newArgs.strip()        
    getRunInfo(host, path, "detail")
    if getTestFramework(host, path) == 'pygash':
        getRunInfoForPygash(host, path)
    
    aCounts = getPFSCounts(host, path)
    aPass = aCounts['num_pass']
    fail = aCounts['num_fail']
    skip = aCounts['num_skip']
    inRunning = isJobRunning(host, here_url)

    if inRunning:
        if open(f"{here_non_url}/startupStage"):
            startStage = get_file_content(f"{here_non_url}/startupStage", 1)
        if strpos(startStage, "POST") != False:
            print("<tr><td class=content><a href=\"$here_url\">$result_id</a></td>\n")
            # print("<td align='center' class=content id='"id."' onMouseover=\"over2($id, '$img_loc')\"  onMouseout=\"out($id, '$img_loc')\">  $masterlog_link  <img id='".id."' src='http://$myhost/status/result_index/img/M.png' alt='Master Log' /></a></td>")
            # print("<td class=content>$version</td>")
            # print("<td class=content>$args</td>")
	        # print("<td class=content><font color=green>$startStage</font></td>")

        else:
            if open(f"{here_non_url}/masterlog.html"):
                print("<tr><td class=content><a href=\"$here_url\">$result_id</a></td>\n")
                # echo "<td align='center' id='".++$id."' onMouseover=\"over2($id, '$img_loc')\"  onMouseout=\"out($id, '$img_loc')\">  $masterlog_link <img id='".++$id."' src='http://$myhost/status/result_index/img/M.png' alt='Master Log' /></a></td>";
                # echo "<td class=content>$version</td>";
                # echo "<td class=content>$args</td>";
                # echo "<td class=content>
                #     <font class=pass>$pass</font>/
                #     <font class=fail>$fail</font>/
                #     <font class=skip>$skip</font>
                #     </td>";

    deferrData = {}
    fileToFind = "deferredKill_suite"
    fileName = f"/{host}{path}{fileToFind}"
    if open(fileName):
        deferrData['type'] = "test"
        message = get_file_content(fileName, 0).strip()
        fileStuff = message.split(" ")
        deferrData['name'] = fileStuff[1]
    
    if systemBed:
        aSubCounts = getPFSSubCounts()
        if getTestFramework(host, path) == 'pygash':
            aSubCounts = getIndexPFSCountsForPygash(host, path)
        sub_pass = aSubCounts['num_pass']
        sub_fail = aSubCounts['num_fail']
        print('''
            <td class=content>
                <table border=0>
                <tr><td class=title_bar>So far:</td>
                <td class=content align=center><font class=pass_1>$pass</font>/
                <font class=fail_1>$fail</font>/
                <font class=skip_1>$skip</font></td></tr>
                <tr><td class=title_bar>SubTest:</td>
                <td class=content align=center><font class=pass_1>$sub_pass</font>/
                <font class=fail_1>$sub_fail</font></td></tr>
                <tr><td class=title_bar>Processing:</td>
                <td class=content><a href=http://$myhost$location$result_id/test_console.txt>$current_suite::$current_test</a></td></tr>
                <tr><td class=title_bar>SubTest:</td><td> $currentSubTest</td></tr>
                <tr><td class=title_bar>Time Left:</td><td class=content><font >$time_left</font></td></tr><tr><td class=title_bar>Test Left:</td><td class=content><font >$test_left</font></td></tr></table></td>
        ''')

    else:
        if getTestFramework(host, path) == 'pygash':
            aSubCounts = getIndexPFSCountsForPygash(host, path)
            pass_ = aSubCounts['num_pass']
            fail = aSubCounts['num_fail']
            skip = aSubCounts['num_fail']
        print('''
            <tr><td class=content><a href=\"$here_url\">$result_id</a></td>\n
            <td align='center' class=content id='".++$id."' onMouseover=\"over2($id, '$img_loc')\"  onMouseout=\"out($id, '$img_loc')\">  $masterlog_link  <img id='".++$id."' src='http://$myhost/status/result_index/img/M.png' alt='Master Log' /></a></td>
            <td class=content>$version</td>
            <td class=content>$args</td>
        ''')

        if isJobRunning:
            startStage = "N/A..."
            if open(f"{here_non_url}/startupStage"):
                startStage = get_file_content(f"{here_non_url}/startupStage")
            print("<td class=content><font color=green>$startStage</font></td>")
        else:
            print('''
                "<td class=content>
                <font class=pass>0</font>/
                <font class=fail>0</font>/
                <font class=skip>0</font>
                </td>"
            ''')

def debug(debug_var):
    file_put_contents("/tmp/php_debug.txt", debug_var)