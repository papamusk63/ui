from distutils.log import error
from distutils.util import subst_vars
from itertools import count
from nis import match
import os
import re
from unittest import result, suite
from wsgiref.handlers import format_date_time

from jmespath import search

def calculate(test_dir, file):
    global host_ip
    global errors
    global test_times
    global suite_times
    global failed_url
    global total_proc
    global pass_proc
    global fail_proc
    global skip_proc
    global current_test; 
    global current_suite
    global begin_time
    global overall

    master_log = f"{test_dir}/{file}"
    current_test = ""
    total_proc = 0
    pass_proc = 0
    fail_proc = 0
    skip_proc = 0
    t_suf = ""
    s_suf = ""
    current_suite = ""

    stream = open(master_log, 'r')

    if stream is None:
        return
    for line in stream:
        if current_suite is None:
            current_suite = "initial"
        if current_test is None:
            current_test = "SuiteSetup::initial"
        
        matches = []
        if re.search('/BEGIN ::TestDB::Test([^: \f\n\r\t\v]+)::(.*)/', line, matches):
            if matches[2] == "initial" or matches[2] == "finished":
                current_suite = matches[2]
                current_test = matches[1] + "::" + matches[2]
            elif matches[1] == "Suite":
                current_suite = matches[2]
                the_suite = current_suite.stripe()
                if suite_times[the_suite]['result']:
                    s_suf = s_suf + " "
                    current_suite = current_suite + s_suf
                suite_times[current_suite]['result'] = 'ip'
                current_test = ""

                for suite_name in suite_times:
                    if suite_name['result'] == "ip":
                        suite_times[suite_name]['result'] = "pass"
                    elif suite_times['result'] == "ip-1":
                        suite_times[suite_name]['result'] = "fail"
            
            elif matches[1] == "SuiteCleanup" or matches[1] == "SuiteSetup":
                current_suite = matches[1] + "::" + matches[2]
            else:
                current_test = matches[2]
                the_name = current_test.stripe()
                if test_times[current_suite][the_name]['result']:
                    t_suf = t_suf + " "
                    current_test = current_test + t_suf
                test_times[current_suite][current_test][result] = "ip"

        elif re.search('/BEGIN: Regression Run began at (.*)/', line, matches):
            begin_time = matches[1]
        elif re.search('/BEGIN: (\S+) (\S+) (\S+) (\d+) (\d+):(\d+):(\d+) (\S+) (\d+)/', line, matches):
            begin_time = matches[1] + " " + matches[2] + " " + matches[3] + " " + matches[4] + " " + matches[5] + ":" + matches[6] + ":" + matches[7] + " " + matches[8] + " " + matches[9]
        
        elif re.search('/CRIT: (.*)/', line, matches) or re.search('/ERROR: (.*)/', line, matches):
            if errors[current_suite][current_test]: continue
            test_times[current_suite][current_test]['result'] = "err"
            suite_times[current_suite]['result'] = "ip-1"
            errors[current_suite][current_test] = matches[0]
        
        elif re.search('/RESULT: (\S+): Test Case(\s+)(\S+)/i', line, matches):
            the_test = matches[3]
            the_name = current_test.strip()
            if the_name == the_test:
                if matches[1] == "PASSED":
                    test_times[current_suite][current_test]['result'] = "pass"
                elif matches[1] == "SKIPPED":
                    test_times[current_suite][current_test]['result'] = "skip"
                else:
                    if test_times[current_suite][current_test]['result'] != 'err':
                        test_times[current_suite][current_test]['result'] = 'fail'
                        suite_times[current_suite]['result'] = 'fail'
            else:
                total_proc = total_proc + 1
                if matches[1] == 'PASSED':
                    test_times[current_suite][current_test]['sub'][the_test] = "pass"
                    pass_proc = pass_proc + 1
                elif matches[1] == 'FILED':
                    test_times[current_suite][current_test]['sub'][the_test] = "fail"
                    test_times[current_suite][current_test]['result'] = "fail"
                    suite_times[current_suite]['result'] = "fail"
                    fail_proc = fail_proc + 1
                elif matches[1] == "SKIPPED":
                    test_times[current_suite][current_test]['sub'][the_test] = 'skip'
                    skip_proc = skip_proc + 1

        elif re.search('/END ::TestDB::Test([^: \f\n\r\t\v]+)::(.*)/', line, matches):
            the_test = matches[3]
            the_name = current_test.strip()
            if the_name == the_test:
                if matches[1] == "PASSED":
                    test_times[current_suite][current_test]['result'] = "pass"
                elif matches[1] == "SKIPPED":
                    test_times[current_suite][current_test]['result'] = "skip"
                else:
                    if test_times[current_suite][current_test]['result'] != 'err':
                        test_times[current_suite][current_test]['result'] = 'fail'
                        suite_times[current_suite]['result'] = 'fail'
            else:
                total_proc = total_proc + 1
                if matches[1] == 'PASSED':
                    test_times[current_suite][current_test]['sub'][the_test] = "pass"
                    pass_proc = pass_proc + 1
                elif matches[1] == 'FILED':
                    test_times[current_suite][current_test]['sub'][the_test] = "fail"
                    test_times[current_suite][current_test]['result'] = "fail"
                    suite_times[current_suite]['result'] = "fail"
                    fail_proc = fail_proc + 1
                elif matches[1] == "SKIPPED":
                    test_times[current_suite][current_test]['sub'][the_test] = 'skip'
                    skip_proc = skip_proc + 1

        if os.path.exists("masterlog.html"):
            lines = open("index.html")
            flag = 0
            failed_t = 0
            failed_s = 0
            matches = []

            for line in lines:
                if re.search('/Overall Regression Status: (.*)\</', line, matches):
                    overall = matches[1]
                if re.search('/Hyperlinks for failed tests/', line):
                    flag = 1
                    continue
                if flag and re.search('/(\S+)\<UL\>/', line, matches):
                    if re.search('/Suite/', matches[1]):
                        failed_t = matches[1]
                    else:
                        sub_matches = []
                        if re.search('/Test(.*)/', matches[1], sub_matches):
                            failed_t = sub_matches[1]
                    
                    for t_list, suite in test_times:
                        failed_s = suite
                        if test_times[failed_s][failed_t]['result'] != "fail" and test_times[failed_s][failed_t]['result'] != "err":
                            test_times[failed_s][failed_t]['result'] = "fail_msg"
                            suite_times[failed_s][failed_t]['result'] = "fail"
                    flag = 2
                
                if flag == 2 and re.search('/\<LI\>\<A HREF=\"(.*)\"\>(.*)\<\/A\>/', line, matches):
                    failed_url[failed_s][failed_t] = matches[2] or matches[1]



def running(test_dir):
    global host_ip
    global host
    inprogress = 0

    if os.path.exists(f"/{host}/jobs/inprogress"):
        lines = open(f"/{host}/jobs/inprogress")
        matches = []
        for line in lines:
            if re.search('/Follow the results at(\s+): (.*)/', line, matches):
                job = matches[2].stripe()
                if test_dir == job:
                    inprogress = 1
    
    return inprogress

def get_completed(test_dir):
    global test_times
    global suite_times
    global current_suite
    global total_act
    global latest_complete_time
    global host

    path = strstr(test_dir, "results")
    so_far = f"/{host}/{path}/completedTestList"

    lines = open(so_far)

    s_suf = ""
    t_suf = ""
    count = 0
    suite_matches = []
    for line in lines:
        if re.search('/[a-zA-Z0-9]/', line):
            if current_suite:
                suite_times[current_suite]['act'] = format_time_reverse(suite_time)
            continue
        if re.search('/::TestSuite::(.*)/', line, suite_matches):
            current_suite =tmp[0]
            the_suite = current_suite.stripe()
            if (suite_times[the_suite]['act']):
                   s_suf = s_suf + " "
                   current_suite = current_suite + s_suf
            suite_time = 0
            latest_complete_time =tmp[2]

def get_estimate(test_dir):
    global test_times
    global suite_times
    global total_est
    global host

    # this is a hack to get the old GUI's (other than the status GUI) to behave and play
    # nice with authentication. We cannot use a http string anymore, we are already local
    # when this is called, so I strip off the http junk.
    # look for the first appearance of results string and slam that onto the host string

    path = strstr(test_dir, "results")
    intended = f"/{host}/{path}/intendedTestList"
    lines = open(intended)

    for line in lines:
        if re.search('/[a-zA-Z0-9]/', line):
            if current_suite:
                suite_times[current_suite]['est'] = format_time_reverse (suite_time)
                s_count = s_count + 1
            continue
        suite_matches = []
        if re.search('/::TestSuite::(.*)/', line, suite_matches):
            tmp = suite_matches[1].split("/ /")
            current_suite = tmp[0]
            if test_times and current_suite in test_times:
                s_suf = s_suf + " "
                current_suite = current_suite + s_suf
            suite_time = 0
        else:
            matches = line.split('/\"/')
            name = matches.split('/::Test/')
            name = name.stripe()
            if test_times:
                if test_times[current_suite][name]:
                    t_suf = t_suf + " "
                    name = name + t_suf
            test_times[current_suite][name]['est'] = matches[1]
            time_in_sec = format_date_time(matches[1])
            suite_time = suite_time + time_in_sec
            total_est = total_est + time_in_sec
            count = count + 1
        
        if current_suite == 'finished':
            suite_time[current_suite]['est'] = format_date_time(suite_time)
    
    total_est = format_date_time(total_est)

def check_null(number):
    if number is None:
        number = 0
    return number