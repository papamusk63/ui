from ast import arg
from common_func import *
from common_func import getIndexPFSCounts 
from time_left import *
import os
import re

def livesearch(request):
    q = request["q"]

    referred = False
    if request['HTTP_REFERER'].find("result.php") == -1:
        referred = True
    
    myhost = request['HTTP_HOST']
    host = ('hostname -s').strip()
    # rowserver variable only exists on rowservers, serving virtual beds
    rowserver = os.getenv('ROWSERVER')

    if rowserver == host:
        #we need the virtual host name iso the rowserver
        temp = request['SERVER_NAME']
    
    # obtain local site from /usr/global/regression/LOCALE
    here = getLocale()

    # obtain all testbed info from regress.params
    aTb = FillTestbedArray("/usr/global/bin/regress.params", here)

    host_ip = aTb[host]['IP']
    if host_ip:
        host_ip = host
    
    systemBed = 0
    if aTb[host]['BEDTYPE'] == "systemTest":
        systemBed = 1
    
    note = aTb[host]['DESCRIPTION']

    # definition for the favicon
    print("<link rel=\"shortcut icon\" href=\"http://$myhost/status/images/favicon.ico\">\n")

    if referred:
        uri = request['REQUEST_URI']
        myUrl = f"http://{myhost}{uri}"
        print("<script type='text/javascript' src='overlib.js'><!-- overLIB (c) Erik Bosrup --></script>")
        print("<script type='text/Javascript' src='results_index.js'></script>\n")
        print("<link rel=\"stylesheet\" type=\"text/css\" href=\"http://$myhost/status/css/test.css\">\n")

    else:
        myUrl = request['HTTP_REFERER']
    
    print(f"<title>{q} @ {host}</title>")

    if referred is not None:
        print("<div id=\"overDiv\" style=\"position:absolute; visibility:hidden; z-index:1000;\"></div>\n")
    
    if systemBed is not None:
        print('''
            <table width=100%><tr>
                <td class=\"content_center\" colspan=\"3\"><a href=\"index.php\" style=\"color: #FFFFFF\" title=\"Status Page\">Status</a></td>
                <td class=\"content_center\" colspan=\"10\"><a href=\"http://$myhost/status/result.php\" style=\"color:#FFFFFF; font-size: 12pt\"><i>Results: $host</i></a></td>
                <td class=\"content_center\" colspan=\"3\"><a href=\"/jobs/jobs_index.php\" style=\"color: #FFFFFF\" title=\"Jobs\">Jobs</a></td>
            </tr>
            <tr>
                <td style=\"color: #7B37B3; font-size: 12pt; font-weight: bold\" align=center colspan=16><i>Indexed @ $q</i></td>
            </tr>
            <tr>
                <th class=\"title_bar\" width=\"10%\">Test Run</th>
                <th class=\"title_bar\" width=\"4%\">Checked</th>
                <th class=\"title_bar\" width=\"4%\">Log</th>
                <th class=\"title_bar\" width=\"14%\">Test/Scenario</th>
                <th class=\"title_bar\" width=\"10%\">Submit Reason</th>
                <th class=\"title_bar\" width=\"4%\">DTS</th>
                <th class=\"title_bar\" width=\"5%\">Load Version</th>
                <th class=\"title_bar\" width=\"4%\">Platform</th>
                <th class=\"title_bar\" width=\"4%\">IGP</th>
                <th class=\"title_bar\" width=\"4%\">Sub Topology</th>
                <th class=\"title_bar\" width=\"4%\">Mixed Mode</th>
                <th class=\"title_bar\" width=\"4%\">SSH XML</th>
                <th class=\"title_bar\" width=\"5%\">Results</th>
                <th class=\"title_bar\" width=\"4%\">Traces</th>
                <th class=\"title_bar\" width=\"5%\">Overall</th>
                <th class=\"title_bar\" width=\"15%\">Failure Reason</th>
            </tr>\n
        ''')
    else:
        noteList = f"/{host}/jobs/note_*"
        myNoteCount = len(noteList)
        icon = ""
        if myNoteCount == 1:
            icon = f"http://{myhost}/status/images/sticky-note-pin_single.png"
        elif myNoteCount > 1:
            icon = f"http://{myhost}/status/images/sticky-note-pin_double.png"

        print('''
            <table width=100%>
            <tr>
            <td class=content_center><a href=\"index.php\" style=\"color: #FFFFFF\" title=\"Status Page\">Status</a></td>
        ''')

        if icon == "":
            print('''
                <td class=content_center colspan=\"4\"><a href=\"http://$myhost/status/result.php\" style=\"color:#FFFFFF; font-size: 12pt\"><i>Results: $host</i></a>&nbsp&nbsp($note)</td>
            ''')
        else:
            print('''
                <td class=content_center colspan=\"4\"><a href=\"http://$myhost/status/result.php\" style=\"color:#FFFFFF; font-size: 12pt\"><i>Results: $host</i></a>&nbsp&nbsp(<a href=\"/jobs/jobs_index.php\" style=\"color: #FFFFFF\" title=\"Bed Notes\"><img src=$icon>$note)</a></td>
            ''')

        print('''
            <td class=content_center><a href=\"/jobs/jobs_index.php\" style=\"color: #FFFFFF\" title=\"Jobs\">Jobs</a></td>
            </tr>
            <tr>
            <td style=\"color: #7B37B3; font-size: 12pt; font-weight: bold\" align=center colspan=5><i>Indexed @ $q</i></td>
            </tr>
            <tr>
            <th class=\"title_bar\" width=\"25%\">Test Run</th>
            <th class=\"title_bar\" width=\"5%\">Log</th>
            <th class=\"title_bar\" width=\"10%\">Load Version</th>
            <th class=\"title_bar\" width=\"40%\">Arguments</th>
            <th class=\"title_bar\" width=\"15%\">Pass/Fail/Skip/NoResult</th>
            <th class=\"title_bar\" width=\"5%\">Overall</th></tr>\n
        ''')

        id = 0
        dd = open(".")
        if dd:
            for d in dd:
                if d != "." and d != "..":
                    d_array = d
        
        if os.path.isfile(f"/{host}/jobs/pause"):
            aPauseFile = get_full_file_content(f"/{host}/jobs/pause", 1)
            for tempkey in aPauseFile:
                pause_content = pause_content + aPauseFile[tempkey]
            print('''
                <tr><td align=center><div style='background: #FFCC00; color: #FFFFFF; font-weight: bold' width=100%>
                A pause file has been placed: </div>
                </td>
                <td colspan=5 align=center><div style='background: #FFCC00; color: #FFFFFF; font-weight: bold' width=100%>
                $pause_content
                </div></td>
                </tr>
            ''')
        
global aTestCase
global aTestSuite
global aSubTest
global runStatus
global firstErro

def make_pop_up(desription, caption):
    return f"onmouseover=\"return overlib('$description', TEXTFONTCLASS, 'textFontClass', CAPTION, '$caption');\" onmouseout=\"return nd();\""

def get_content(test_dir, systemBed, myUrl):
    global aTestCase
    global aTestSuite
    global aSubTest
    global myhost
    global host
    global id
    global q
    global runStatus
    global firstError

    dk = ""
    overall = "n/a"

    here_url = f"http://{myhost}/results/{q}/{test_dir}/"
    img_loc = f"http://{myhost}/status/result_index/"
    here_non_url = f"/{host}/results/{q}/{test_dir}"

    version = get_file_content(f"{here_non_url}/version.txt")
    if version is not None:
        version = "n/a"
    
    args = get_file_content(f"{here_non_url}/args")
    if args is not None:
        args = "n/a"
    
    if systemBed:
        testName = ""
        igp = ""
        platform = "7750"
        dts = ""
        subTopology = ""
        ssh = ""
        mixedMode = ""
        submitReason = ""
        bug = ""
        testDirWithoutUser = "$test_dir"
        matches = []

        if re.search('/-framework\s+(\S+)\s*/', args, matches):
            framework = matches[1]

        if re.search('/-framework\s+(\S+)\s*/', args, matches):
            reason = matches[1]

        if re.search('/-platform\s+(\S+)\s*/', args, matches):
            platform = matches[1]

        if re.search('/-framework\s+(\S+)\s*/', args, matches):
            reason = matches[1]

        if re.search('/-bug\s+(\S+)\s*/', args, matches):
            bug = matches[1]

        if re.search('/-framework\s+(\S+)\s*/', args, matches):
            reason = matches[1]

        if re.search('/-originalTestName\s+(\S+)\s*/', args, matches):
            testName = matches[1]

        if re.search('/-subTopology\s+(\S+)\s*/', args, matches):
            subTopology = matches[1]

        if re.search('/-reason\s+(\S+)\s*/', args, matches):
            submitReason = matches[1]

        if re.search('/-ssh\s+true\s*/', args, matches):
            ssh = "SSH"

        if re.search('/-useXml\s+true\s*/', args, matches):
            ssh = "SSH"

        if re.search('/-ssh\s+true\s*/', args, matches):
            ssh = "SSH\nXML"

        if re.search('/-mixedMode\s+true\s*/', args, matches):
            ssh = "SSH\nXML"
        
        failReason = ""
        fileName = f"{here_non_url}/failureReason"
        
        # strip off the -idleBedStartingUp, could be anywhere
        aArgs = args.split(" ")
        newArgs = ""

        args = newArgs.strip()
        orig = args

        isRunning = isRunning(host, here_url)
        path = f"/results/{q}/{test_dir}/"

        if isRunning is not None:
            # for efficiency, if not running only chew on index.html for PFS counts
            aCounts = getIndexPFSCounts(host, path)
            pass_ = aCounts['num_pass']
            fail = aCounts['num_fail']
            skip = aCounts['num_skip']
            noResult = aCounts['num_no_result']
            runStatus = aCounts['status']


        if systemBed:
            f'''
                echo "<tr><td class=content><a href=\"$here_url\">$testDirWithoutUser</a></td>\n";
                echo "<td class=content>$checkBox</td>";
                echo "<td align='center' class=content id='".++$id."' onMouseover=\"over2($id, '$img_loc')\" onMouseout=\"out($id, '$img_loc')\">  <a href='$here_url/$masterlog_index'>  <img id='".++$id."' src='http://$myhost/status/result_index/img/M.png' alt='Master Log'></a></td>";
                echo "<td class=content $output>$testName</td>";
                echo "<td class=content>$submitReason</td>";
                echo "<td class=content><a href=\"http://dts.mv.usa.alcatel.com/cgi-bin/dts9/viewReport.cgi?report_id=$bug\">$bug</a></td>";
                echo "<td class=content>$version</td>";
                echo "<td class=content>$platform</td>";
                echo "<td class=content>$igp</td>";
                echo "<td class=content>$subTopology</td>";
                echo "<td class=content>$mixedMode</td>";
                echo "<td class=content>$ssh</td>";
            '''
        
        if isRunning is None:
            if os.path.isfile(f"{here_non_url}/deferredKill_suite"):
                reason = get_file_content("here_non_url/deferredKill_suite", 1)
                overall = "Killed"
                text = (reason).strip()
                string_pieces = explode ("|", text)
                reason = string_pieces[0]
                suite = string_pieces[1]
                msg = make_pop_up("Regression was killed after suite: <font color=green> $suite: $reason </font>", "Reason")
            elif os.path.isfile(f"{here_non_url}/deferredKill_test"):
                reason = get_file_content("here_non_url/deferredKill_test", 1)
                overall = "Killed"
                text = (reason).strip()
                string_pieces = explode ("|", text)
                reason = string_pieces[0]
                test = string_pieces[1]
                msg = make_pop_up("Regression was killed after test case: <font color=green> $test: $reason </font>", "Reason")
            elif os.path.isfile(f"{here_non_url}/kill_9"):
                reason = get_file_content("here_non_url/kill_9", 1)
                overall = "Killed"
                text = trim(reason)
                string_pieces = explode ("|", text)
                reason = string_pieces[0]
                test = string_pieces[1]
                msg = make_pop_up("Regression was Aggressively killed: <font color=green> $reason when executing $test </font>", "Reason")

            print('''
                <td class=content>
                <font class=pass>$pass</font>/
                <font class=fail>$fail</font>/
                <font class=skip>$skip</font>/
                <font class=no_result>$noResult</font>
                </td>
            ''')

            