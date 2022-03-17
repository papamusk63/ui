#!/usr/bin/php

<html>
<head>

<script type="text/javascript">
    function setCookie() {
        // get the checkbox value
        var checked = 0;
        if (document.myform2.sub.checked) {
            var checked = 1;
        }
        var cookieValue = checked;
        // set the cookie
        createCookie('SrGuiSubTest',cookieValue,0);
        // reload the page with the new settings
        javascript:location.reload(true);
    }
     function createCookie(name,value,days) {
      if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
      }
      else var expires = "";
        document.cookie = name+"="+value+expires+"; path=/";
    }
</script>

<?php

#error_reporting(1);

# -------------- #
# Initialization #
# -------------- #
$myhost = $_SERVER['HTTP_HOST'];
$host = trim(`hostname -s`);
# rowserver variable only exists on rowservers, serving virtual beds
$rowserver = getenv('ROWSERVER');
if ($rowserver == $host) {
       #we need the virtual host name iso the rowserver
       $temp = $_SERVER['SERVER_NAME'];
       list($host, $domain_not_wanted) = explode('.', $temp, 2);
     }
# else we are in a non-virtual environment -- do nothing: host var is ok as is

include "/$host/status/time_left.php";
include "/$host/status/read_masterlog2.php";
include "/$host/status/common_func.php";

# obtain all testbed info from regress.params
$aTb = FillTestbedArray("/usr/global/bin/regress.params");

$host_ip = $aTb[$host]['IP'];
if (!$host_ip) {
    $host_ip = $host;
}
$note = htmlspecialchars($aTb[$host]['DESCRIPTION']);
unset($aTb);

$sim_logs = array();
$id = 0;
$js_loc = "http://$myhost/status/masterlog/js/masterlog.js";
$css_loc = "http://$myhost/status/masterlog/css/masterlog.css";
$img_loc = "http://$myhost/status/masterlog/";
$location = getenv('REQUEST_URI');
$loc_parts = preg_split('/\//', $location);
$test_dir = "/$host$loc_parts[0]/$loc_parts[1]/$loc_parts[2]/$loc_parts[3]/$loc_parts[4]/$loc_parts[5]/";
$path = "$loc_parts[0]/$loc_parts[1]/$loc_parts[2]/$loc_parts[3]/$loc_parts[4]/$loc_parts[5]/";
$results_index = "/$host$loc_parts[0]/$loc_parts[1]/$loc_parts[2]/$loc_parts[3]/$loc_parts[4]/";
$test_dir_url = "http://$myhost$loc_parts[0]/$loc_parts[1]/$loc_parts[2]/$loc_parts[3]/$loc_parts[4]/$loc_parts[5]/";

echo "<link rel=\"shortcut icon\" href=\"http://$myhost/status/images/favicon.ico\">\n";
echo "<script language=\"JavaScript\" src=\"$js_loc\"></script>\n";
echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"$css_loc\">\n";
echo "<title>[$host]: ".$loc_parts[4]."_".$loc_parts[2]."/".$loc_parts[5]."</title>\n";
echo "</head><body>\n";

# do we have a sub test cookie set?
$sGroup = "All";
$bSubTest = 1;
if (isset($_COOKIE['SrGuiSubTest'])) {
    $sSelectCookie = $_COOKIE['SrGuiSubTest'];
    if ($sSelectCookie != "") {
        $aInfo = explode(" ", $sSelectCookie);
        $bSubTest = $aInfo[0];
    }
}
chdir("$test_dir");

# ---- #
# MAIN #
# ---- #
$dd = @opendir(".");
if ($dd) {
    while (false !== ($d = @readdir($dd))) {
        if ($d != "." && $d != ".." && is_file($d)) {
            $d_array[]= $d;
        }
    }
}

global $aTestSuite;
global $aTestCase;
global $aSubTest;

if (file_exists("$test_dir/intendedTestList")) {
  foreach ($d_array as $file) {
      if (preg_match('/(ESR|WMM)\.([^.]+)\.(.*)\.(html|txt)/', $file, $matches)) {
            if (!isset($sim_logs[$matches[1]][$matches[2]])) {
                $sim_logs[$matches[1]][$matches[2]][$matches[3]] = 1;
            } else {
                $sim_logs[$matches[1]][$matches[2]][$matches[3]] ++;
            }
        }
        if ($file == "masterlog.txt") {
            getRunInfo($host, $path, "detail");
        }
      if ($file == "version.txt") {
          $version = get_file_content("$test_dir/$file");
        }
      if ($file == "args") {
          $args = get_file_content("$test_dir/$file");
        }
  }
}
# do we have notes
$noteList = glob("/$host/jobs/note_*");
$myNoteCount = count($noteList);
$icon = "";
if ($myNoteCount == 1) {
    $icon = "http://$myhost/status/images/sticky-note-pin_single.png";
} elseif ($myNoteCount > 1) {
    $icon = "http://$myhost/status/images/sticky-note-pin_double.png";
}
echo "<table>
    <tr>
        <td class=content_center2><a href=\"http://$myhost/status/index.php\" target=\"_top\" style=\"color: #FFFFFF; font-weight: bold\" title=\"Status Page\">Status</a></td>";

if ($icon == "") {
    echo "<td class=content_center2><a href=\"http://$myhost/status/result.php\" target=\"_top\" style=\"color:#FFFFFF; font-weight: bold\">Result Index</a>&nbsp&nbsp($note)</td>";
} else {
    echo "<td class=content_center2><a href=\"http://$myhost/status/result.php\" target=\"_top\" style=\"color:#FFFFFF; font-weight: bold\">Result Index</a>&nbsp&nbsp(<a href=\"/jobs/jobs_index.php\" style=\"color: #FFFFFF\" title=\"Bed Notes\"><img src=$icon>$note)</td>";
}

echo "<td class=content_center2><a href=\"http://$myhost/jobs/jobs_index.php\" target=\"_top\" style=\"color: #FFFFFF; font-weight: bold\" title=\"Jobs\">Jobs</a></td>
    </tr>
    <tr>
        <td class=normal_med align=center colspan=3><i>[$host]: ".$loc_parts[4]."_".$loc_parts[2]."/".$loc_parts[5]."</i></td>
        </tr></table>";

# ------------------------ #
# Top bar: links - Sim Log #
# ------------------------ #
echo "<hr><table border=1><tr><td class=normal><a href=$test_dir_url title=$test_dir_url ><img src=$img_loc/img/node.jpg /></a></td>\n";
$sim_logs = natksort($sim_logs);
foreach ($sim_logs as $product => $nodes) {
    echo "            <td class=title_bar>$product</td>\n";
    $nodes = natksort($nodes);
    foreach ($nodes as $node => $cards) {
        echo "            <td class=title_bar>$node</td><td class=_small>";
        $cards = natksort($cards);
        foreach ($cards as $card => $num) {
            # keep these guys for later
            $sims[] = "$product.$node.$card.txt";
            if ($num == 1) {
                $the_url = $test_dir_url."$product.$node.$card.txt";
                echo "<a href=$the_url title=$the_url>$card</a> ";
            } else {
                $the_url = $test_dir_url."$product.$node.$card.html";
                echo "<a href=$the_url title=$the_url >$card</a> ";
            }
        }
        echo "</td>\n";
    }
}
echo "        </tr></table><hr>";

# fill in all of the pass fail summary data
$total_est = format_time_reverse(getSuiteTotal('est'));
$total_act = format_time_reverse(0);
$aSuiteCounts = getPFSSuiteCounts();
$aCounts = getPFSCounts($host, $path);
$aSubCounts = getPFSSubCounts();
$pass = $aCounts['num_pass'];
$fail = $aCounts['num_fail'];
$skip = $aCounts['num_skip'];
$noResult = $aCounts['num_no_result'];
$total_test = count($aTestCase);
$total_suite = count($aTestSuite);
$total_proc = count($aSubTest);
$total_tp = $total_test + $total_proc;
$pass_suite = $aSuiteCounts['num_pass'];
$fail_suite = $aSuiteCounts['num_fail'];
$skip_suite = $aSuiteCounts['num_skip'];
$noResult_suite = $aSuiteCounts['num_no_result'];
$pass_sub = $aSubCounts['num_pass'];
$fail_sub = $aSubCounts['num_fail'];
$skip_sub = $aSubCounts['num_skip'];
$noResult_sub = $aSubCounts['num_no_result'];
$pass_tp =  $pass + $pass_sub;
$fail_tp =  $fail + $fail_sub;
$skip_tp = $skip + $skip_sub;
$noResult_tp = $noResult + $noResult_sub;


$deferrData = array();
# do we have a deferr file?
$fileToFind = "deferredKill_suite";
$fileName = "/$host$path$fileToFind";
$deferrData['type'] = "";
if (file_exists($fileName)) {
    $deferrData['type'] = "suite";
}
$fileToFind = "deferredKill_test";
$fileName = "/$host$path$fileToFind";
if (file_exists($fileName)) {
    $deferrData['type'] = "test";
    $message = trim(get_file_content($fileName, 0));
    if (strpos($message, "afterNamedTest") !== false) {
        $fileStuff = explode(" ", $message);
        $deferrData['name'] = $fileStuff[1];
    }
}

$timing_info = getTimingInfo($deferrData);
$isRunning = isRunning($host, $test_dir_url);
# everything is new now
#$newReport = determineVer($host, $path);

if ($isRunning) {
    if (isset($aTestSuite[1]['starttime'])) {
        $total_act = format_time_reverse(time() - $aTestSuite[1]['starttime']);
    }
    $curStatus = "<font color=green><b>passing...</b></font>";
    if ($fail > 0) {
        $curStatus = "<font color=red><blink><b>failing...</b></blink></font>";
    }
    if (isset($timing_info['running_test_time_remaining'])) {
        if ($timing_info['running_test_time_remaining'] < 0) {
            $overtime = $timing_info['running_test_time_remaining'] * -1;
            $time_left = "<font color=#BDB76B>".format_time_reverse($timing_info['suite_time_remaining'])." + <font color=red>".format_time_reverse($overtime)." exceeding est. duration</font>";
        } else {
            $time_left = format_time_reverse($timing_info['suite_time_remaining']);
        }
    } else {
        if (!isset($timing_info['running_test_name'])) {
            $timing_info['running_test_name'] = "Unknown";
        }
        $overtime = $timing_info['running_test_time_remaining'] * -1;
        $time_left = "<font color=#BDB76B>".format_time_reverse($timing_info['suite_time_remaining'])."</font> + <font color=red> ".format_time_reverse($overtime)." current duration unknown </font>";
    }
} else {
    $total_act = format_time_reverse(getSuiteTotal('act'));
    $aCounts = getIndexPFSCounts($host, $path);
    $runStatus = $aCounts['status'];
    if (strpos($runStatus, "FAIL") === false) {
        $curStatus = "<font color=green><b>PASSED</b></font>";
    } else {
        $curStatus = "<font color=red><blink><b>FAILED</b></blink></font>";
    }
    $time_left = format_time_reverse(0);
}

echo "<table border=3>
  <tr>
        <td class=normal_big><i>$loc_parts[5]</i></td>
    <td class=normal_hl width=20%><i>$version</i></td>
    <td class=normal_hl colspan=2><i>$args</i></td>
  </tr>
  <tr>
        <td class=title_bar width=200>Total Est. Time:</td><td class=normal>$total_est</td>
        <td class=title_bar>Num Suites: Total (P/F/S/NA)</td>
        <td class=normal_big>$total_suite (<font color=green>$pass_suite</font> / <font color=red>$fail_suite</font> / <font color=gray>$skip_suite</font> / <font color=orange>$noResult_suite</font>)</td>
    </tr>
  <tr>
        <td class=title_bar width=200>Actual Time:</td><td class=normal>$total_act</td>
        <td class=title_bar>Num Tests (no subtests): Total (P/F/S/NA)</td>
      <td class=normal_big>$total_test (<font color=green>$pass</font> / <font color=red>$fail</font> / <font color=gray>$skip</font> / <font color=orange>$noResult</font>)</td>
    </tr>
  <tr>
        <td class=title_bar width=200>Est. Remaining:</td><td class=normal>$time_left</td>
        <td class=title_bar>Num Tests (with subtests): </td>
        <td class=normal_big>$total_tp (<font color=green>$pass_tp</font> / <font color=red>$fail_tp</font> / <font color=gray>$skip_tp</font>)</td>
    </tr>
  <tr>
        <td class=title_bar width=200>Status:</td><td class=normal>$curStatus</td>
        <td class=title_bar>Num Subtests:</td>
        <td class=normal_big>$total_proc (<font color=green>$pass_sub</font> / <font color=red>$fail_sub</font> / <font color=gray>$skip_sub</font>)</td>
  </tr>
         <td class=note colspan=2>* &nbsp</font>TC: test_console log &nbsp &nbsp ML: masterlog</td>";

# the sub test check box
if (!$bSubTest) {
    echo "<td class=note colspan=2><FORM NAME='myform2' action=''><font size=2>Display Sub Test Detail?</font><input type='checkbox' name='sub' onClick='setCookie()'></FORM></td></tr></table>";
} else {
    echo "<td class=note colspan=2><FORM NAME='myform2' action=''><font size=2>Display Sub Test Detail?</font><input type='checkbox' name='sub' onClick='setCookie()' checked></FORM></td></tr></table>";
}

echo "<table><tr><td class=_small_title><b></b></td>
    <td class=_small_title align='left'><b>Name</b></td>
    <td class=_small_title><b>TC</b></td>
    <td class=_small_title><b>ML</b></td>
    <td class=_small_title><b>Estimated</b></td>
    <td class=_small_title><b>Actual</b></td>
    <td class=_small_title><b>Result</b></td></tr>";

# common suite column settings
$cs1 = "<td align=right class=normal_med><i>Suite</i></td>";
$cs3 = "<td class=normal_med colspan=2></td>";

# common test column settings
$ct3b = "<td align=center><img src=".$img_loc."img/nav_normal_2.png title=\"Test Console Log\"></a></td>";
$ct4b = "<td align=center><img src=".$img_loc."img/nav_normal_2.png title=\"Masterlog\"></a></td>";
$na = "<td class=test_na></td>";

# default to test_console 1, others will incr
$indx = 1;

# the Suite rows
foreach (array_keys($aTestSuite) as $key) {
    $suite = $aTestSuite[$key]['name'];
    $est = format_time_reverse($aTestSuite[$key]['est']);
    $act = format_time_reverse($aTestSuite[$key]['act']);
    if (isset($aTestSuite[$key]['result'])) {
        $suite_result = $aTestSuite[$key]['result'];
    }
    # common suite column settings
    $cs2 = "<td align=left class=normal_med><i>$suite</i></td>";
    $cs4 = "<td align=center class=normal_med><i>$est</i></td>";
    $cs5 = "<td align=center class=normal_med><i>$act</i></td>";

    if ($timing_info['current_suite_id'] > $key) {
        # finished suites
        echo "<tr> $cs1 $cs2 $cs3 $cs4 $cs5";
        # TBD - what to do if no result?
        if (isset($aTestSuite[$key]['result'])) {
            if ($aTestSuite[$key]['result'] == "PASSED") {
                echo "<td class=normal_med align=center><font color=green>PASSED</font></td>";
            } else {
                echo "<td class=normal_med align=center><font color=red><blink>FAILED</blink></font></td>";
            }
            echo "</tr>";
        }
    } else if ($timing_info['current_suite_id'] < $key) {
        # suites not started yet
        if (!didSomethingRun($key)) {
          echo "<tr><td align=right class=normal_med_2><i>Suite</i></td>
            <td align=left class=normal_med_2><i>$suite</i></td>
            <td class=normal_med_2 colspan=2></td>
            <td align=center class=normal_med_2><i>$est</i></td>
                <td align=center class=normal_med_2><i>$act</i></td>
                <td class=normal_med_2 align=center>pending...</td></tr>";
        } else {
            # probably the cleanup suite, colour it done
            echo "$cs1 $cs2 $cs3 $cs4 $cs5";
            # TBD - what to do if no result?
            if (isset($aTestSuite[$key]['result'])) {
                if ($aTestSuite[$key]['result'] == "PASSED") {
                    echo "<td class=normal_med align=center><font color=green>PASSED</font></td>";
                } else {
                    echo "<td class=normal_med align=center><font color=red><blink>FAILED</blink></font></td>";
                }
                echo "</tr>";
            }
        }
    } else {
        # the busy suite
        echo "$cs1 $cs2 $cs3 $cs4 $cs5";
        if (isset($aTestSuite[$key]['result'])) {
            if ($aTestSuite[$key]['result'] == "FAILED") {
                if ($isRunning) {
                    echo "<td class=normal_med align=center><font color=red><blink>failing...</blink></font></td>";
                } else {
                    echo "<td class=normal_med align=center><font color=red><blink>FAILED</blink></font></td>";
                }
            } else {
                if ($isRunning) {
                    echo "<td class=normal_med align=center><font color=green>passing...</font></td>";
                } else {
                    echo "<td class=normal_med align=center><font color=green>PASSED</font></td>";
                }
            }
        } else {
            if ($isRunning) {
                echo "<td class=normal_med align=center><font color=green>passing...</font></td>";
            } else {
                echo "<td class=normal_med align=center>pending...</td>";
            }
        }
        echo "</tr>";
    }
    # the test rows associated with the suite
    foreach (array_keys($aTestCase) as $key2) {
        # this is cheating, relying on the fact that everything is in order
        if ($aTestCase[$key2]['suite'] != $key) {
            break;
        }
        if (isset($aTestCase[$key2]['console_indx'])) {
            $indx = $aTestCase[$key2]['console_indx'];
        }
        unset($t_result_txt);
        unset($t_result);
        unset($t_console);
        unset($m_console);
        unset($t_est);
        unset($t_act);
        $testName = $aTestCase[$key2]['name'];
        if ($aTestCase[$key2]['est'] != "unknown") {
            $t_est = format_time_reverse_nice($aTestCase[$key2]['est']);
        } else {
            $t_est = $aTestCase[$key2]['est'];
        }
        if (isset($aTestCase[$key2]['result'])) {
            $t_result = $aTestCase[$key2]['result'];
        }

        # old logs not using the new createreport do this
      if (preg_match('/::/', $testName)) {
            $attach = "TestSuite".$testName;
        } else {
            $attach = $testName;
        }
        $tAttach = "T$key2";
        $mAttach = 0;
        if (isset($aTestCase[$key2]['lineNum'])) {
            $mAttach = $aTestCase[$key2]['lineNum'];
        }

        # need to know if the html results were from the old CreateReport or the new createReport
        # time to remove this, everything is new for quite some time now
        #if ($newReport) {
            if ($indx != "none") {
                $t_console = $test_dir_url."test_console." . $indx . ".html#".$tAttach;
            } else {
                $t_console = $test_dir_url."test_console.html#".$tAttach;
            }
            $m_console = $test_dir_url."masterlog.html#".$mAttach;
        #} else {
        #    $t_console = $test_dir_url."test_console.html#".$attach;
        #    $m_console = $test_dir_url."masterlog.html#".$attach;
        #}
        # if its running now, point them at the txt file
        if ($isRunning) {
            $t_console = $test_dir_url."test_console.txt";
            $m_console = $test_dir_url."masterlog.txt";
        }

        # more common test column settings
        $ct3 = "<td id='".++$id."' align=center onMouseover=\"over($id, '$img_loc')\" onMouseout=\"out($id, '$img_loc')\" align=left><a href=$t_console title=\"Test Console Log\" ><img id=".++$id." src=".$img_loc."img/nav_normal.png title=\"Test Console Log\"></img></a></td>";
        $ct4 = "<td id='".++$id."' align=center onMouseover=\"over($id, '$img_loc')\" onMouseout=\"out($id, '$img_loc')\" align=left><a href=$m_console title=\"Masterlog\" ><img id=".++$id." src=".$img_loc."img/nav_normal.png title=\"Masterlog\"></img></a></td>";

        # has it run yet?
        if ((!$isRunning) or ($key2 < $timing_info['current_test_id'])) {
            if (!isset($aTestCase[$key2]['result'])) {
          echo "<tr>
                    <td align=right><font color=#C1A4A4>$key2</font></td>
                    <td align=left><font color=#ACB7C4>$testName</font></td>
                  $ct3b $ct4b
                    <td align=center><font color=#ACB7C4>$t_est</font></td>
                    $na $na
                    </tr>";

            } else {
              echo "<tr>
                    <td align=right><font color=#7347AD>$key2</font></td>
                    <td align=left>$testName</td>
                    $ct3 $ct4
                  <td align=center>$t_est</td>";
                if (isset($aTestCase[$key2]['act'])) {
                    if ($aTestCase[$key2]['act'] != "aborted") {
                        $t_act = format_time_reverse_nice($aTestCase[$key2]['act']);
                    } else {
                        $t_act = $aTestCase[$key2]['act'];
                    }
                    echo "<td align=center>$t_act</td>";
                } else {
                    echo "$na";
                }
                if (isset($aTestCase[$key2]['url']) or isset($aTestCase[$key2]['error'])) {
                    if (isset($aTestCase[$key2]['error'])) {
                        $theError = $aTestCase[$key2]['error'];
                        $t_result_txt = "$theError<br>";
                    } else {
                        $t_result_txt = "<img src=".$img_loc."img/failed.png><br>";
                    }
                    if (isset($aTestCase[$key2]['url'])) {
                        $msg_url_list = $aTestCase[$key2]['url'];
                        foreach ($msg_url_list as $key4 => $msg_url) {
                            $parts = preg_split('/\|/',$msg_url);
                            if (!$isRunning) {
                                $t_result_txt .= "<img src=".$img_loc."img/failed_msg.png><a href=$test_dir_url$parts[1]>$parts[0]</a><br>";
                            } else {
                                $t_result_txt .= "<img src=".$img_loc."img/failed_msg.png><a href=$m_console>masterlog.txt</a><br>";
                            }
                        }
                    }
                    echo "<td class=error align=center >$t_result_txt</td>";
                } else {
                if ($t_result == "PASSED") {
                    echo"<td class=test_passed></td>";
                  } else if ($t_result == "FAILED") {
                        echo "<td class=test_failed></td>";
                  } else if ($t_result == "SKIPPED") {
                        echo "<td class=skipped align=center>SKIPPED</td>";
                } else {
                        echo "$na";
                    }
                }
                echo "</tr>";
            }
        } else if ($timing_info['current_test_id'] == $key2) {
            # running now
            $t_act = format_time_reverse_nice($timing_info['running_test_running_time']);
            echo "<tr>
                <td align=right ><img src=".$img_loc."img/processing.gif></td>
                <td align=left><font color=#333333 size=4px><B><i>$testName</i></B></font></td>
                $ct3 $ct4
                <td align=center><font color=#333333 size=2px><i><B>$t_est</B></i></font></td>
                <td align=center>$t_act<img src=".$img_loc."img/processing_2.gif></td>
                <td align=center><img src=".$img_loc."img/processing_2.gif></td>
                </tr>";
        } else {
            # not running yet
      echo "<tr>
                <td align=right><font color=#C1A4A4>$key2</font></td>
                <td align=left><font color=#ACB7C4>$testName</font></td>
                $ct3b $ct4b
                <td align=center><font color=#ACB7C4>$t_est</font></td>
                $na $na
                </tr>";
        }
        # the sub tests for the current test
        if ($bSubTest && isset($aSubTest)) {
            foreach (array_keys($aSubTest) as $key3) {
                unset($t_result_txt2);
                if ($aSubTest[$key3]['test'] == $key2) {
                    if (isset($aSubTest[$key3]['url']) or isset($aSubTest[$key3]['error'])) {
                        if (isset($aSubTest[$key3]['error'])) {
                            $theError = $aSubTest[$key3]['error'];
                            $t_result_txt2 = "$theError<br>";
                        }
                        if (isset($aSubTest[$key3]['url'])) {
                            $msg_url_list2 = $aSubTest[$key3]['url'];
                            foreach ($msg_url_list2 as $key5 => $msg_url2) {
                                $parts2 = preg_split('/\|/',$msg_url2);
                                if (!$isRunning) {
                                    $t_result_txt2 .= "<img src=".$img_loc."img/failed_msg.png><a href=$test_dir_url$parts2[1]>$parts2[0]</a><br>";
                                } else {
                                    $t_result_txt2 .= "<img src=".$img_loc."img/failed_msg.png><a href=$m_console>masterlog.txt</a><br>";
                                }
                            }
                        }
                        $proc_result = "<td class=error align=center >$t_result_txt2</td>";
                    } else {
                  if ($aSubTest[$key3]['result'] == "PASSED") {
                            $proc_result = "<td class=proc_passed></td>";
                        } else if ($aSubTest[$key3]['result'] == "FAILED") {
                            $proc_result = "<td class=proc_failed></td>";
                        } else if ($aSubTest[$key3]['result'] == "SKIPPED") {
                            $proc_result = "<td class=skipped align=center>SKIPPED</td>";
                        }
                    }
                    $proc_name = $aSubTest[$key3]['name'];
            echo "<tr>
                        <td align=right><font color=#AA8A8C size=1px>$key3</font></td>
                        <td align=left><font color=#A49BD2>&nbsp &nbsp $proc_name</font></td>
                        $ct3 $ct4 $na $na $proc_result
                        </tr>";
                }
            }
        }
        # this helps performance, diminishes the test list
        unset($aTestCase[$key2]);
    }
}

echo "</table>";
?>

<br><br></body></html>