from aiohttp import RequestInfo
from time_left import *
from read_masterlog import *
from common_func import *
import os
import re


def masterlog2(request):
    myhost = request['HTTP_HOST']
    host = ('hostname -s').strip()

    rowserver = os.getenv('ROWSERVER')
    if rowserver == host:
        temp = request['SERVER_NAME']
        host = temp.split('.')
    user = request['GUIAuth']
    if user == "":
        user = "Unknown User"
    
    # obtain all testbed info from regress.params
    aTb = FillTestbedArray("/usr/global/bin/regress.params")
    host_ip = aTb[host]['IP']
    if host_ip:
        host_ip = host
    note = htmlspecialchars(aTb[host]['DESCRIPTION'])

    sim_logs = []
    id = 0
    js_loc = "http://myhost/status/masterlog/js/masterlog.js"
    css_loc = "http://myhost/status/masterlog/css/masterlog.css"
    img_loc = "http://myhost/status/masterlog/"

    location = request['HTTP_REFERER']
    loc_parts = re.search('/\//', location)
    test_dir = "/host/loc_parts[3]/loc_parts[4]/loc_parts[5]/loc_parts[6]/loc_parts[7]/"
    test_dir_url = "http://myhost/loc_parts[3]/loc_parts[4]/loc_parts[5]/loc_parts[6]/loc_parts[7]/"
    path = "/loc_parts[3]/loc_parts[4]/loc_parts[5]/loc_parts[6]/loc_parts[7]/"
    results_index = "/host/loc_parts[3]/loc_parts[4]/loc_parts[5]/loc_parts[6]/"

    print('''
        echo "<link rel=\"shortcut icon\" href=\"http://myhost/status/images/favicon.ico\">\n"
        echo "<script type=\"text/JavaScript\" src=\"js_loc\"></script>\n"
        #echo "<script language=\"JavaScript\" src=\"js_loc\"></script>\n"
        echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"css_loc\">\n"
        echo "<title>[host]: ".loc_parts[5]."_".loc_parts[4]."/".loc_parts[6]."</title>\n"
        echo "</head><body>\n"
        echo "<script type=\"text/Javascript\" src=\"http://myhost/status/masterlog/js/overlib/overlib.js\"></script>\n"
    ''')

    sGroup = "All"
    bSubTest = 1
    if request['SrGuiSubTest']:
        sSelectCookie = request['SrGuiSubTest']
        if sSelectCookie = "":
            aInfo = sSelectCookie.split(".")
            bSubTest = aInfo[0]
    
    dd = open(".")
    if dd:
        d_array = dd
     
    global aTestSuite
    global aTestClass
    global aTestCase
    global aSubTest

    intended = f"{test_dir}/intendedTestList"
    if getTestFramework(host, path) == 'pygash': 
        intended = f"{test_dir}/pygash_logs/intendedTestList"
        getRunInfoForPygash(host, path)
    
    args = get_file_content(f"{test_dir}/args")
    if os.path.isfile(args):
        for d_array in file:
            if (preg_match('/(ESR|WMM)\.([^.]+)\.(.*)\.(html|txt)/', file, matches)):
                if (isset(sim_logs[matches[1]][matches[2]])):
                    sim_logs[matches[1]][matches[2]][matches[3]] = 1
                else:
                    sim_logs[matches[1]][matches[2]][matches[3]]
            if (file == "masterlog.txt"):
                getRunInfo(host, path, "detail")
            if (file == "version.txt"):
                version = get_file_content("test_dir/file")

    if (getTestFramework(host, path) == 'pygash'):
        version = get_file_content("test_dir/version.txt")
        args = get_file_content("test_dir/args")
    
    # do we have notes
    noteList = glob("/host/jobs/note_*")
    myNoteCount = count(noteList)
    icon = ""
    if (myNoteCount == 1):
        icon = "http://myhost/status/images/sticky-note-pin_single.png"
    elif (myNoteCount > 1):
        icon = "http://myhost/status/images/sticky-note-pin_double.png"
    print('''<table>
        <tr>
            <td class=content_center2><a href=\"http://myhost/status/index.php\" target=\"_top\" style=\"color: #FFFFFF font-weight: bold\" title=\"Status Page\">Status</a></td>"
    ''')
    if (icon == ""):
        print("<td class=content_center2><a href=\"http://myhost/status/result.php\" target=\"_top\" style=\"color:#FFFFFF font-weight: bold\">Result Index</a>&nbsp&nbsp(note)</td>")
    else:
        print("<td class=content_center2><a href=\"http://myhost/status/result.php\" target=\"_top\" style=\"color:#FFFFFF font-weight: bold\">Result Index</a>&nbsp&nbsp(<a href=\"/jobs/jobs_index.php\" style=\"color: #FFFFFF\" title=\"Bed Notes\"><img src=icon>note)</td>")

    # sim_logs = natksort(sim_logs)
    # foreach (sim_logs as product => nodes):
    #     echo "            <td class=title_bar>product</td>\n"
    #     nodes = natksort(nodes)
    #     foreach (nodes as node => cards):
    #         echo "            <td class=title_bar>node</td><td class=_small>"
    #         cards = natksort(cards)
    #         foreach (cards as card => num):
    #             # keep these guys for later
    #             sims[] = "product.node.card.txt"
    #             if (num == 1):
    #                 the_url = test_dir_url."product.node.card.txt"
    #                 echo "<a href=the_url title=the_url>card</a> "
    #              else:
    #                 the_url = test_dir_url."product.node.card.html"
    #                 echo "<a href=the_url title=the_url >card</a> "


    #         echo "</td>\n"

    


    # fill in all of the pass fail summary data
    total_est = format_time_reverse(getSuiteTotal('est'))
    total_act = format_time_reverse(0)
    aSuiteCounts = getPFSSuiteCounts()
    aCounts = getPFSCounts(host, path)
    aSubCounts = getPFSSubCounts()
    pass_ = aCounts['num_pass']
    fail = aCounts['num_fail']
    skip = aCounts['num_skip']
    noResult = aCounts['num_no_result']
    total_test = count(aTestCase)
    total_suite = count(aTestSuite)
    total_proc = count(aSubTest)
    total_tp = total_test + total_proc
    pass_suite = aSuiteCounts['num_pass']
    fail_suite = aSuiteCounts['num_fail']
    skip_suite = aSuiteCounts['num_skip']
    noResult_suite = aSuiteCounts['num_no_result']
    pass_sub = aSubCounts['num_pass']
    fail_sub = aSubCounts['num_fail']
    skip_sub = aSubCounts['num_skip']
    noResult_sub = aSubCounts['num_no_result']
    pass_tp =  pass_ + pass_sub
    fail_tp =  fail + fail_sub
    skip_tp = skip + skip_sub
    noResult_tp = noResult + noResult_sub


    
    #Check if run has been killed
    runKilled = False

    deferrData = array()
    # do we have a deferr file?
    fileToFind = "deferredKill_suite"
    fileName = "/hostpathfileToFind"
    deferrData['type'] = ""
    if (file_exists(fileName)):
        deferrData['type'] = "suite"
        runKilled = True
    
    fileToFind = "deferredKill_test"
    fileName = "/hostpathfileToFind"
    if (file_exists(fileName)):
        deferrData['type'] = "test"
        runKilled = True
        message = trim(get_file_content(fileName, 0))
        if (strpos(message, "afterNamedTest") = False) :
            fileStuff = explode(" ", message)
            deferrData['name'] = fileStuff[1]

    fileToFind = "kill_9"
    fileName = "/hostpathfileToFind"
    if (file_exists(fileName)):
        runKilled = True

    timing_info = getTimingInfo(deferrData)
    isRunning = isRunning(host, test_dir_url)

    
    if (isRunning):
        if (isset(aTestSuite[1]['starttime'])):
            total_act = format_time_reverse(time() - aTestSuite[1]['starttime'])

        curStatus = "<font color=green><b>passing...</b></font>"
        if ( runKilled == True ):
            curStatus = "<font color=red><blink><b>killing...</b></blink></font>"
        else:
            if (fail > 0):
                curStatus = "<font color=red><blink><b>failing...</b></blink></font>"


        if (isset(timing_info['running_test_time_remaining'])):
            if (timing_info['running_test_time_remaining'] < 0):
                overtime = timing_info['running_test_time_remaining'] * -1
                time_left = "<font color=#BDB76B>".format_time_reverse(timing_info['suite_time_remaining'])." + <font color=red>".format_time_reverse(overtime)." exceeding est. duration</font>"
            else:
                time_left = format_time_reverse(timing_info['suite_time_remaining'])

        else:
            if (isset(timing_info['running_test_name'])):
                timing_info['running_test_name'] = "Unknown"

            overtime = timing_info['running_test_time_remaining'] * -1
            time_left = "<font color=#BDB76B>".format_time_reverse(timing_info['suite_time_remaining'])."</font> + <font color=red> ".format_time_reverse(overtime)." current duration unknown </font>"

    else:
        total_act = format_time_reverse(getSuiteTotal('act'))
        aCounts = getIndexPFSCounts(host, path)
        if ( runKilled == True ):
            curStatus = "<font color=red><blink><b>KILLED</b></blink></font>"
        else:
            runStatus = aCounts['status']
            if (strpos(runStatus, "FAIL") == False):
                curStatus = "<font color=green><b>PASSED</b></font>"
            else:
                curStatus = "<font color=red><blink><b>FAILED</b></blink></font>"


        time_left = format_time_reverse(0)

    
    print('''
        <table border=3>
        <tr>
            <td class=normal_big><i>loc_parts[7]</i></td>
            <td class=normal_hl width=20%><i>version</i></td>
            <td class=normal_hl colspan=2><i>args</i></td>
        </tr>
        <tr>
            <td class=title_bar width=200>Total Est. Time:</td><td class=normal>total_est</td>
            <td class=title_bar>Num Suites: Total (P/F/S/NA)</td>
            <td class=normal_big>total_suite (<font color=green>pass_suite</font> / <font color=red>fail_suite</font> / <font color=gray>skip_suite</font> / <font color=#FF8040>noResult_suite</font>)</td>
        </tr>
        <tr>
            <td class=title_bar width=200>Actual Time:</td><td class=normal>total_act</td>
            <td class=title_bar>Num Tests (no subtests): Total (P/F/S/NA)</td>
            <td class=normal_big>total_test (<font color=green>pass</font> / <font color=red>fail</font> / <font color=gray>skip</font> / <font color=#FF8040>noResult</font>)</td>
        </tr>
        <tr>
            <td class=title_bar width=200>Est. Remaining:</td><td class=normal>time_left</td>
            <td class=title_bar>Num Tests (with subtests): </td>
            <td class=normal_big>total_tp (<font color=green>pass_tp</font> / <font color=red>fail_tp</font> / <font color=gray>skip_tp</font>)</td>
        </tr>
        <tr>
            <td class=title_bar width=200>Status:</td><td class=normal>curStatus</td>
            <td class=title_bar>Num Subtests:</td>
            <td class=normal_big>total_proc (<font color=green>pass_sub</font> / <font color=red>fail_sub</font> / <font color=gray>skip_sub</font>)</td>
        </tr>
            <td class=note colspan=2>* &nbspTC: test_console log &nbsp &nbsp ML: masterlog</td>"
    ''')

    
    # the sub test check box
    if (bSubTest):
        print("<td class=note colspan=2><FORM NAME='myform2' action=''><font size=2>Display Sub Test Detail?</font><input type='checkbox' name='sub' onClick='setCookie()'></FORM></td></tr></table>")
    else:
        print("<td class=note colspan=2><FORM NAME='myform2' action=''><font size=2>Display Sub Test Detail?</font><input type='checkbox' name='sub' onClick='setCookie()' checked></FORM></td></tr></table>")
    #resubmit
    if (isRunning == False):
        ps = "<form action=http://myhost/status/cgi_scripts/resubmit.cgi method=GET onsubmit=\'return check_args(this)\'  target=_top><table border=1 width=500px><tr><input type=hidden name=host value=host><input type=hidden name=user value=user><input type=hidden name=host_ip value=host_ip><input type=hidden name=myhost value=myhost><input type=hidden name=test_dir value=test_dir><td class=title_bar width=200>Resubmit this: </td><td class=content_2><textarea name=arguments cols=80>args</textarea></td></tr><tr><td class=content colspan=3><input type=submit value=OK></td></tr></table></form>"
        output = make_pop_up(ps)
        print("<tr><td class=content_2 align=center colspan=2><input type=submit output value='Resubmit'></td></tr>")
    
    print('''
        <table><tr><td class=_small_title></td>
        <td class=_small_title align='left'><b>Name</b></td>
        <td class=_small_title><b>TC</b></td>
        <td class=_small_title><b>ML</b></td>
        <td class=_small_title><b>Estimated</b></td>
        <td class=_small_title><b>Actual</b></td>
        <td class=_small_title><b>Result</b></td></tr>
    ''')

    cs1 = "<td align=right class=normal_med><i>Suite</i></td>"
    cs3 = "<td class=normal_med colspan=2></td>"

    # common class column settings (used for pygash runs)
    cc1 = "<td align=right><font color=purple><b>Test</b></font></td>"

    # common test column settings
    ct3b = "<td align=center><img src=".img_loc."img/nav_normal_2.png title=\"Test Console Log\"></a></td>"
    ct4b = "<td align=center><img src=".img_loc."img/nav_normal_2.png title=\"Masterlog\"></a></td>"
    na = "<td class=test_na></td>"

    # default to test_console 1, others will incr
    indx = 1

def make_pop_up (description):
    return "onclick=\"return overlib('description',TEXTFONTCLASS,'textFontClass',CAPTIONFONTCLASS,'capfontClass2',CLOSEFONTCLASS,'capfontclass2',CAPTION,'Details',STICKY)\" onclick=\"return nd()\""

prev_test_class= ""


# the Suite rows
foreach (array_keys(aTestSuite) as key) {
    suite = aTestSuite[key]['name']
    est = format_time_reverse(aTestSuite[key]['est'])
    act = format_time_reverse(aTestSuite[key]['act'])
    if (isset(aTestSuite[key]['result'])) {
        suite_result = aTestSuite[key]['result']
    }
    # more common suite settings
    cs2 = "<td align=left class=normal_med><i>suite</i></td>"
    cs4 = "<td align=center class=normal_med><i>est</i></td>"
    cs5 = "<td align=center class=normal_med><i>act</i></td>"

    if (timing_info['current_suite_id'] > key) {
        # finished suites
        echo "<tr> cs1 cs2 cs3 cs4 cs5"
        # TBD - what to do if no result?
        if (isset(aTestSuite[key]['result'])) {
            if (aTestSuite[key]['result'] == "PASSED") {
                echo "<td class=normal_med align=center><font color=green>PASSED</font></td>"
            } else {
                echo "<td class=normal_med align=center><font color=red><blink>FAILED</blink></font></td>"
            }
            echo "</tr>"
        }
    } else if (timing_info['current_suite_id'] < key) {
        # suites not started yet
        if (isset(aTestSuite[key]['testRan'])) {
	        echo "<tr><td align=right class=normal_med_2><i>Suite</i></td>
		        <td align=left class=normal_med_2><i>suite</i></td>
		        <td class=normal_med_2 colspan=2></td>
		        <td align=center class=normal_med_2><i>est</i></td>
                <td align=center class=normal_med_2><i>act</i></td>
                <td class=normal_med_2 align=center>pending...</td></tr>"
        } else {
            # probably the cleanup suite, colour it done
            echo "cs1 cs2 cs3 cs4 cs5"
            # TBD - what to do if no result?
            if (isset(aTestSuite[key]['result'])) {
                if (aTestSuite[key]['result'] == "PASSED") {
                    echo "<td class=normal_med align=center><font color=green>PASSED</font></td>"
                } else {
                    echo "<td class=normal_med align=center><font color=red><blink>FAILED</blink></font></td>"
                }
                echo "</tr>"
            }
        }
    } else {
        # the busy suite
        echo "cs1 cs2 cs3 cs4 cs5"
        if (isset(aTestSuite[key]['result'])) {
            if (aTestSuite[key]['result'] == "FAILED") {
                if (isRunning) {
                    echo "<td class=normal_med align=center><font color=red><blink>failing...</blink></font></td>"
                } else {
                    echo "<td class=normal_med align=center><font color=red><blink>FAILED</blink></font></td>"
                }
            } else {
                if (isRunning) {
                    echo "<td class=normal_med align=center><font color=green>passing...</font></td>"
                } else {
                    echo "<td class=normal_med align=center><font color=green>PASSED</font></td>"
                }
            }
        } else {
            if (isRunning) {
                echo "<td class=normal_med align=center><font color=green>passing...</font></td>"
            } else {
                echo "<td class=normal_med align=center>pending...</td>"
            }
        }
        echo "</tr>"
    }
    # the test rows associated with the suite
    foreach (array_keys(aTestCase) as key2) {
        # this is cheating, relying on the fact that everything is in order
        if (aTestCase[key2]['suite'] = key) {
            break
        }
        if (isset(aTestCase[key2]['console_indx'])) {
            indx = aTestCase[key2]['console_indx']
        }
        unset(t_result_txt)
        unset(t_result)
        unset(t_console)
        unset(m_console)
        unset(t_est)
        unset(t_act)
        testName = aTestCase[key2]['name']
        if (aTestCase[key2]['est'] = "unknown") {
            t_est = format_time_reverse_nice(aTestCase[key2]['est'])
        } else {
            t_est = aTestCase[key2]['est']
        }
        if (isset(aTestCase[key2]['result'])) {
            t_result = aTestCase[key2]['result']
        }

        # old logs not using the new createreport do this
    	if (preg_match('/::/', testName)) {
            attach = "TestSuite".testName
        } else {
            attach = testName
        }
        tAttach = "Tkey2"
        mAttach = 0
        if (isset(aTestCase[key2]['lineNum'])) {
            mAttach = aTestCase[key2]['lineNum']
        }

        # need to know if the html results were from the old CreateReport or the new createReport
        # time to remove this, everything is new for quite some time now
        #if (newReport) {
        if (indx = "none") {
           t_console = test_dir_url."test_console." . indx . ".html#".tAttach
        } else {
            t_console = test_dir_url."test_console.html#".tAttach
        }
        if (getTestFramework(host, path) == 'pygash') {
                        suite_num = aTestCase[key2]['suite']
                        suite_name = aTestSuite[suite_num]['name']
                        mAttach = "pygash/suite/".suite_name
                        t_console = test_dir_url.mAttach
        }
        m_console = test_dir_url."masterlog.html#".mAttach
        #} else {
        #    t_console = test_dir_url."test_console.html#".attach
        #    m_console = test_dir_url."masterlog.html#".attach
        #}
        # if its running now, point them at the txt file
        if (isRunning) {
            t_console = test_dir_url."test_console.txt"
            m_console = test_dir_url."masterlog.txt"
            if (getTestFramework(host, path) == 'pygash') {
                        t_console = test_dir_url."pygash/console"
                    }
        }

        # more common test column settings
        ct3 = "<td id='".++id."' align=center onMouseover=\"over(id, 'img_loc')\" onMouseout=\"out(id, 'img_loc')\"><a href=t_console title=\"Test Console Log\" ><img id=".++id." src=".img_loc."img/nav_normal.png title=\"Test Console Log\"></a></td>"
        ct4 = "<td id='".++id."' align=center onMouseover=\"over(id, 'img_loc')\" onMouseout=\"out(id, 'img_loc')\"><a href=m_console title=\"Masterlog\" ><img id=".++id." src=".img_loc."img/nav_normal.png title=\"Masterlog\"></a></td>"
        if (getTestFramework(host, path) == 'pygash') {
            ct4 = "<td ></td>"
            ct4b = "<td ></td>"
        }
        # pygash specific handling
        test_class = aTestCase[key2]['test_class']
        suite = aTestCase[key2]['suite']
        if (isset(aTestClass[suite][test_class]) && aTestClass[suite][test_class]['name'] = "") {
            # print class name
           test_class_name = aTestClass[suite][test_class]['name']
           if (prev_test_class = test_class_name) {
                prev_test_class = test_class_name

                cc2 = "<td align=left colspan=3><font color=purple><b>test_class_name</b><font></td>"
                est = format_time_reverse(aTestClass[suite][test_class]['est'])
                act = format_time_reverse(aTestClass[suite][test_class]['act'])
                # more common class settings
                cc3 = "<td align=center><font color=purple><b>est</b></font></td>"
                cc4 = "<td align=center><font color=purple><b>act</b></font></td>"
                cc_pass = "<td align=center><font color=green><b>PASSED</b></font></td>"
                cc_fail = "<td align=center><font color=red><blink><b>FAILED</b></blink></font></td>"
                cc_failing = "<td align=center><font color=red><blink></b>failing...</b></blink></font></td>"
                cc_passing = "<td align=center><font color=green>passing...</font></td>"
                cc_pending = "<td align=center><font><b>pending...</b></font></td>"

                # checking the status
                curr_class_id = aTestCase[timing_info['current_test_id']]['test_class']

                if (curr_class_id > test_class) {
                    # finished suites
                    echo "<tr> cc1 cc2 cc3 cc4"
                    # TBD - what to do if no result?
                    if (isset(aTestClass[suite][test_class]['result'])) {
                        if (aTestClass[suite][test_class]['result'] == "PASSED") {
                            echo cc_pass
                        } else {
                            echo cc_fail
                        }
                    }
                    echo "</tr>"
                } else if (curr_class_id < test_class) {
                    # testclass not started yet
                    if (isset(aTestClass[suite][test_class]['testRan'])) {
                        echo "<tr><td align=right class=normal_med_2><font size=2><i>Test</i></font></td>
                            <td align=left class=normal_med_2 colspan=3><font size=2><i>test_class_name</i></font></td>
                            <td align=center class=normal_med_2><font size=2><i>est</i></font></td>
                            <td align=center class=normal_med_2><font size=2><i>act</i></font></td>
                            <td class=normal_med_2 align=center><font size=2>pending...</font></td></tr>"
                    } else {
                        # probably the cleanup suite, colour it done
                        echo "cc1 cc2 cc3 cc4"
                        # TBD - what to do if no result?
                        if (isset(aTestClass[suite][test_class]['result'])) {
                            if (aTestClass[suite][test_class]['result'] == "PASSED") {
                                echo cc_pass
                            } else {
                                echo cc_fail
                            }
                        }
                        echo "</tr>"
                    }
                } else {
                    # the busy class
                    echo "cc1 cc2 cc3 cc4"
                    if (isset(aTestClass[suite][test_class_id]['result'])) {
                        if (aTestClass[suite][test_class_id]['result'] == "FAILED") {
                            if (isRunning) {
                                echo cc_failing
                            } else {
                                echo cc_fail
                            }
                        } else {
                            if (isRunning) {
                                echo cc_passing
                            } else {
                                echo cc_pass
                            }
                        }
                    } else {
                        if (isRunning) {
                            echo cc_passing
                        } else {
                            echo cc_pending
                        }
                    }
                    echo "</tr>"
                }
            }
            # retain only testcase name, strip off module and class info
            # to avoid printing empty testcase name
            if (testName = test_class_name) {
                testName = trim(str_replace(test_class_name, "", testName), '.')
            }
        }

        # has it run yet?
        if ((isRunning) or (key2 < timing_info['current_test_id'])) {
            if (isset(aTestCase[key2]['result'])) {
			    echo "<tr>
                    <td align=right><font color=#C1A4A4>key2</font></td>
                    <td align=left><font color=#ACB7C4>testName</font></td>
	                ct3b ct4b
          	        <td align=center><font color=#ACB7C4>t_est</font></td>
                    na na
   	                </tr>"

            } else {
     	        echo "<tr>
                    <td align=right><font color=#7347AD>key2</font></td>
                    <td align=left>testName</td>
                    ct3 ct4
        	        <td align=center>t_est</td>"
                if (isset(aTestCase[key2]['act'])) {
                    if (aTestCase[key2]['act'] = "aborted") {
                        t_act = format_time_reverse_nice(aTestCase[key2]['act'])
                    } else {
                        t_act = aTestCase[key2]['act']
                    }
                    echo "<td align=center>t_act</td>"
                } else {
                    echo "na"
                }
                if (isset(aTestCase[key2]['url']) or isset(aTestCase[key2]['error'])) {
                    if (isset(aTestCase[key2]['error'])) {
                        theError = aTestCase[key2]['error']
                        t_result_txt = "theError<br>"
                    } else {
                        t_result_txt = "<img src=".img_loc."img/failed.png><br>"
                    }
                    if (isset(aTestCase[key2]['url'])) {
                        msg_url_list = aTestCase[key2]['url']
                        foreach (msg_url_list as key4 => msg_url) {
                            parts = preg_split('/\|/',msg_url)
                            if (isRunning) {
                                t_result_txt .= "<img src=".img_loc."img/failed_msg.png><a href=test_dir_urlparts[1]>parts[0]</a><br>"
                            } else {
                                t_result_txt .= "<img src=".img_loc."img/failed_msg.png><a href=m_console>masterlog.txt</a><br>"
                            }
                        }
                    }
                    echo "<td class=error align=center >t_result_txt</td>"
                } else {
		            if (t_result == "PASSED") {
	        	        echo"<td class=test_passed></td>"
        	        } else if (t_result == "FAILED") {
                        echo "<td class=test_failed></td>"
	                } else if (t_result == "SKIPPED") {
                        echo "<td class=skipped align=center>SKIPPED</td>"
		            } else {
                        echo "na"
                    }
                }
                echo "</tr>"
            }
        } else if (timing_info['current_test_id'] == key2) {
            # running now
            t_act = format_time_reverse_nice(timing_info['running_test_running_time'])
            echo "<tr>
                <td align=right ><img src=".img_loc."img/processing.gif></td>
                <td align=left><font color=#333333 size=4px><B><i>testName</i></B></font></td>
                ct3 ct4
                <td align=center><font color=#333333 size=2px><i><B>t_est</B></i></font></td>
                <td align=center>t_act<img src=".img_loc."img/processing_2.gif></td>
                <td align=center><img src=".img_loc."img/processing_2.gif></td>
                </tr>"
        } else {
            # not running yet
			echo "<tr>
                <td align=right><font color=#C1A4A4>key2</font></td>
                <td align=left><font color=#ACB7C4>testName</font></td>
                ct3b ct4b
         	    <td align=center><font color=#ACB7C4>t_est</font></td>
                na na
       	        </tr>"
        }
        # the sub tests for the current test
        if (bSubTest && isset(aSubTest)) {
            foreach (array_keys(aSubTest) as key3) {
                tAttachST = "Tkey3"
                t_consoleST = test_dir_url."test_console." . indx . ".html#".tAttachST
                if (getTestFramework(host, path) == 'pygash') {
                        suite_num = aSubTest[key3]['suite']
                        suite_name = aTestSuite[suite_num]['name']
                        t_consoleST = test_dir_url."pygash/suite/".suite_name
                        if(isset(aSubTest[key3]['name']) && trim(aSubTest[key3]['name']) = ""){
                           subtest_name = aSubTest[key3]['name']
                           subtest_name = str_replace(" ", "_", subtest_name)
                           t_consoleST = test_dir_url."pygash/suite/".suite_name."#".subtest_name
                        }
                }
                if (isRunning) {
                    t_consoleST = test_dir_url."test_console.txt"
                    if (getTestFramework(host, path) == 'pygash') {
                        t_consoleST = test_dir_url."pygash/console"
                    }
                }
                unset(t_result_txt2)
                if (aSubTest[key3]['test'] == key2) {
                    if (isset(aSubTest[key3]['url']) or isset(aSubTest[key3]['error'])) {
                        if (isset(aSubTest[key3]['error'])) {
                            theError = aSubTest[key3]['error']
                            t_result_txt2 = "theError<br>"
                        }
                        if (isset(aSubTest[key3]['url'])) {
                            msg_url_list2 = aSubTest[key3]['url']
                            foreach (msg_url_list2 as key5 => msg_url2) {
                                parts2 = preg_split('/\|/',msg_url2)
                                if (isRunning) {
                                    #t_result_txt2 .= "<img src=".img_loc."img/failed_msg.png><a href=test_dir_urlparts2[1]>parts2[0]</a><br>"
                                    t_console_indx = "test_console." . indx . ".html"
                                    t_result_txt2 .= "<img src=".img_loc."img/failed_msg.png><a href=t_consoleST>t_console_indx</a><br>"
                                } else {
                                    t_result_txt2 .= "<img src=".img_loc."img/failed_msg.png><a href=m_console>masterlog.txt</a><br>"
                                }
                            }
                        }
                        proc_result = "<td class=error align=center >t_result_txt2</td>"
                    } else {
			            if (aSubTest[key3]['result'] == "PASSED") {
                            proc_result = "<td class=proc_passed></td>"
                        } else if (aSubTest[key3]['result'] == "FAILED") {
                            proc_result = "<td class=proc_failed></td>"
                        } else if (aSubTest[key3]['result'] == "SKIPPED") {
                            proc_result = "<td class=skipped align=center>SKIPPED</td>"
                        } else if (aSubTest[key3]['result'] == "NOT_RUN") {
                            proc_result = na
                        }
                    }
                   if(isset(aSubTest[key3]['est'])){
                        subtest_est_value = aSubTest[key3]['est']
                        subtest_est ="<td align=center >subtest_est_value<i></i></td>"
                   }else{
                        subtest_est =na
                   }
                   if(isset(aSubTest[key3]['act'])){
                        subtest_act_value = aSubTest[key3]['act']
                        subtest_act ="<td align=center ><i>subtest_act_value</i></td>"
                   }else{
                        subtest_act =na
                   }

                    proc_name = aSubTest[key3]['name']
                        ct3 = "<td id='".++id."' align=center onMouseover=\"over(id, 'img_loc')\" onMouseout=\"out(id, 'img_loc')\" align=left>
                        <a href=t_consoleST title=\"Test Console Log\" ><img id=".++id." src=".img_loc."img/nav_normal.png title=\"Test Console Log\"></img></a></td>"
		        echo "<tr>
                        <td align=right><font color=#AA8A8C size=1px>key3</font></td>
                        <td align=left><font color=#A49BD2>&nbsp &nbsp proc_name</font></td>
                        ct3 ct4 subtest_est subtest_act proc_result
                        </tr>"
                }
            }
        }
        # this helps performance, diminishes the test list
        unset(aTestCase[key2])
    }
}


    