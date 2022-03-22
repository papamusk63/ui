import ip_list
from app.common_func import pingip
from app.ip_list import getIPs, GetBedStatus, GetSpecialNotes, GetToday, CountQueuedJobs, getJobId, getPausedReason, get_idle, get_paused
# import time_left
from app.time_left import get_esimate, get_completed, change_result_index
import common_func
import read_masterlog2
import re
import os.path

# error_reporting(1)

month_hash = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

ip_list = {}
testbed_status = {}
waiting_list = {}
finish_times = {}
pause_reasons = {}
processing_jobs = {}
testbed_dates = {}
testbed_notes = {}
test_times = {}


#  /* GET IP LIST OF TEST BEDS */
getIPs()


me = "hostname -s"
host = ip_list[me]
if host is None:
    host = me

css_loc = "css/quick.css"
overlib_loc = f"http://{host}/status/masterlog/js/overlib/overlib.js"
print(f"<link rel=\"stylesheet\" type=\"text/css\" href={css_loc}>\n")
print(f"<script language=Javascript src={overlib_loc}></script>\n")

GetBedStatus("idle")
GetBedStatus("paused")
GetBedStatus("inprogress")

GetSpecialNotes("/usr/global/bin/regress.data")


busy_beds = {}
idle_beds = {}
paused_beds = {}

for key, val in testbed_dates:
    if ip_list[key]:
        ts_ip = ip_list[key]
    else:
        ts_ip = key
    online = pingip(ts_ip)
    if online is None:
        continue
    GetToday(key)
    CountQueuedJobs(key)
    if val == 'inprogress':
        getJobId(key)
        busy_beds = key
    if val == 'pasued':
        getPausedReason(key)
        paused_beds = key
    if val == 'idle':
        idle_beds = key
    

print("<table  border=1 width=100%>")
if idle_beds:
    print("idle")
    for key in idle_beds:
        get_idle(key)

if busy_beds:
    print("inprogress")
    for key in busy_beds:
        get_inprogress(key)

if paused_beds:
    print("paused")
    for key in paused_beds:
        get_paused(key)


def whatDoINeed(tb):
    global me
    if re.search('/k(an|rtb)/', me) and re.search('/spr/', tb):
        return 1
    elif re.search('/spr/', me) and re.search('/k(an|rtb)/', tb):
        return 1
    else:
        return 0

def GetBedStatus(status):
    global testbed_status
    dir = f"/usr/global/regression/{status}"
    if os.path.isdir(dir):
        fd = open(dir, "r")
        if fd:
            bFound = 0
            dir_list = os.listdir(dir)
            for part in dir_list:
                if part != "." and part != "..":
                    file_array = part
                    bFound = 1
            if bFound == 1:
                file_array.sort()
                file_array.reset()
                for i, val in enumerate(file_array):
                    npart = file_array[i]
                    ignore = 0
                    if ignore:
                        continue
                    fzise = 'unknown'
                    if os.path.isdir(npart) is None:
                        testbed_status[npart] = status

def CountQueuedJobs(bed):
    global waiting_list
    jobsdir=f"http://{bed}/jobs/"

    test_waiting = 0
    lines = open(jobsdir)
    iJobs = 0
    matches = []
    for line in lines:
        if re.search('/<input type=hidden name=test_waiting value=(\d+)>/', line):
            iJobs = matches[1]
    
    waiting_list[bed] = iJobs


def GetCompletionTime(url, jobid):
    global finish_times
    masterfile = f"{url}/masterlog.txt"
    stream = open(masterfile)
    if stream is None:
        finish_times[jobid] = ""
    
    found = 0
    for line in stream:
        matches_time = []
        if re.search( '/Estimated time of regression completion is (.*)\./', line, matches_time ):
            finish_times[jobid] = matches_time[1]
            found = 1

def getPausedReason(bed):
    global pause_reasons
    masterfile = f"http://{bed}/jobs/pause"
    stream = open(masterfile)
    if stream is None:
        pause_reasons[bed] = ""
    
    reason = ""
    for line in stream:
        matches_reason = []
        if re.search( '/.*(\S+).*/', line, matches_reason ):
            reason = matches_reason[0]

    pause_reasons[bed] = reason


def getJobId(bed):
    global processing_jobs
    inprogress = f"http://{bed}/jobs/inprogress"

    lines = open(inprogress)
    for line in lines:
        if line.find("(submitted timestamp)") != 0:
            token = line.find("(submitted timestamp)")
            jobid = line + token
        if line.find("ollow the results)") != 0:
            token = line.find("ollow the results)")
            url = line + token
        if line.find("rguments passed to tests") != 0:
            token = line.find("rguments passed to tests")
            args = line + token
        if line.find("ersion (if known)") != 0:
            token = line.find("ersion (if known)")
            version = line + token

    processing_jobs[bed][jobid] = jobid
    processing_jobs[bed][version] = version
    processing_jobs[bed][args] = args
    processing_jobs[bed][url] = url

    GetCompletionTime(str.strip(url), jobid)

def GetToday(bed):
    global testbed_dates
    daemon = "http://bed/jobs/daemonrunning"
    file = open (daemon, "r")
    if file:
        return "No daemon file found"
    
    line = file[1024]
    date = str.strip(line)
    testbed_dates[bed] = date

def GetSpecialNotes(notes_file):
    global testbed_notes
    lines = open (notes_file)
    for line in lines:
        line = str.strip(line)
        matches_notes = []
        if re.search('/(\S+)(\s+)-(\s+)(.*)/', line, matches_notes):
            bed = matches_notes[1]
            note = matches_notes[4]
            testbed_notes[bed] = note

def check_exist (file):
    exist = open (file, "r")
    r = 0
    if exist:
        r = 1 
    return r

def get_inprogress(bed):
    global testbed_status
    global waiting_list
    global processing_jobs
    global finish_times
    global testbed_dates
    global testbed_notes
    global ip_list
    global test_time

    host = ip_list[bed]
    if host is None:
        host = bed
    job_waiting = waiting_list[bed]
    if job_waiting > 0:
        img = f"<img src=images/job_waiting.gif title=Checkout Detail>"
        if job_waiting > 1:
            s = " jobs waiting"
        else:
            s = " job waiting"
    else:
        img = " "
        s = " job waiting"
    
    waiting_string = f"<a href=http://{host}/jobs/ title=Checkout Detail>{img}{job_waiting}{s}</a>"
    jobid = processing_jobs[bed][jobid]
    joburl = processing_jobs[bed][url]
    version = processing_jobs[bed][version]
    args = processing_jobs[bed][args]
    ft = finish_times[jobid]

    time_left = ""
    log_url = ""
    test_times = ""
    begin_time_sec = 0
    time_left_sec = 0
    remain = 0

    if ft is None:
        time_left = "Pending..."
    else:
        get_esimate(joburl)
        get_completed(joburl)
    
    jobid_new = ( re.search("/@.*/", "", jobid))
    log_url = joburl + "masterlog.php"
    
    daily_summary_url = ( re.search ("/(\d+)\:(\d+).*/", "", joburl))
    change_result_index(daily_summary_url, bed)
    note = testbed_notes[bed]
    if note is None:
        note = "SimPC only"
    print(f"<tr><td class=tb_inprogress>"
          f"<a class=tb href=\"http://{host}/results/\" title={host}>{bed}</a></td>"
          f"<td class=test_name><a href={joburl} title=Result Index>{jobid_new}</a></td>\n"
          f"<td class=time_left>{time_left}</td>\n"
          f"<td class=version>{version}</td>\n"
          f"<td class=args>{args}</td>\n<td class=masterlog>"
          f"<a href={log_url} title=\"Test Log\"><img src=images/mstl.gif></a></td>\n"
          f"<td class=job_waiting>{waiting_string}</td>\n"
          f"<td class=notes>{note}</td></tr>\n")

def get_paused(bed):
    global testbed_status
    global waiting_list
    global processing_jobs
    global finish_times
    global testbed_dates
    global testbed_notes
    global ip_list
    global test_time

    host = ip_list[bed]
    if host is None:
        host = bed
    job_waiting = waiting_list[bed]
    if job_waiting > 0:
        img = f"<img src=images/job_waiting.gif title=Checkout Detail>"
        if job_waiting > 1:
            s = " jobs waiting"
        else:
            s = " job waiting"
    else:
        img = " "
        s = " job waiting"
    
    waiting_string = f"<a href=http://{host}/jobs/ title=Checkout Detail>{img}{job_waiting}{s}</a>"
    jobid = processing_jobs[bed][jobid]
    joburl = processing_jobs[bed][url]
    version = processing_jobs[bed][version]
    args = processing_jobs[bed][args]
    ft = finish_times[jobid]

    time_left = ""
    log_url = ""
    test_times = ""
    begin_time_sec = 0
    time_left_sec = 0
    remain = 0

    if ft is None:
        time_left = "Pending..."
    else:
        get_esimate(joburl)
        get_completed(joburl)
    
    jobid_new = ( re.search("/@.*/", "", jobid))
    log_url = joburl + "masterlog.php"
    
    daily_summary_url = ( re.search ("/(\d+)\:(\d+).*/", "", joburl))
    change_result_index(daily_summary_url, bed)
    note = testbed_notes[bed]
    if note is None:
        note = "SimPC only"
    print(f"<tr><td class=tb_inprogress>"
          f"<a class=tb href=\"http://{host}/results/\" title={host}>{bed}</a></td>"
          f"<td class=test_name><a href={joburl} title=Result Index>{jobid_new}</a></td>\n"
          f"<td class=time_left>{time_left}</td>\n"
          f"<td class=version>{version}</td>\n")


def get_idle(bed):
    global testbed_status
    global waiting_list
    global processing_jobs
    global finish_times
    global testbed_dates
    global testbed_notes
    global ip_list
    global test_time

    host = ip_list[bed]
    if host is None:
        host = bed
    job_waiting = waiting_list[bed]
    if job_waiting > 0:
        img = f"<img src=images/job_waiting.gif title=Checkout Detail>"
        if job_waiting > 1:
            s = " jobs waiting"
        else:
            s = " job waiting"
    else:
        img = " "
        s = " job waiting"
    
    waiting_string = f"<a href=http://{host}/jobs/ title=Checkout Detail>{img}{job_waiting}{s}</a>"
    jobid = processing_jobs[bed][jobid]
    joburl = processing_jobs[bed][url]
    version = processing_jobs[bed][version]
    args = processing_jobs[bed][args]
    ft = finish_times[jobid]

    time_left = ""
    log_url = ""
    test_times = ""
    begin_time_sec = 0
    time_left_sec = 0
    remain = 0

    if ft is None:
        time_left = "Pending..."
    else:
        get_esimate(joburl)
        get_completed(joburl)
    
    jobid_new = ( re.search("/@.*/", "", jobid))
    log_url = joburl + "masterlog.php"
    
    daily_summary_url = ( re.search ("/(\d+)\:(\d+).*/", "", joburl))
    change_result_index(daily_summary_url, bed)
    note = testbed_notes[bed]
    if note is None:
        note = "SimPC only"
    print(f"<tr><td class=tb_inprogress>"
          f"<a class=tb href=\"http://{host}/results/\" title={host}>{bed}</a></td>"
          f"<td class=test_name><a href={joburl} title=Result Index>{jobid_new}</a></td>\n"
          f"<td class=time_left>{time_left}</td>\n"
          f"<td class=version>{version}</td>\n")
    
def print_title(type):
    if type == "idle":
        print('''
            "<tr><td class=title_bar>Test Bed</td>\n
                        <td class=title_bar colspan=5> &nbsp </td>\n
                        <td class=title_bar>Jobs Waiting</td>\n
                        <td class=title_bar>Purpose/Notes</td></tr>\n"
        ''')
    elif type == "inprogress":
        print('''
            <tr><td class=title_bar>Test Bed</td>\n
                        <td class=title_bar>Job</td>\n
                        <td class=title_bar>Time Left</td>\n
                        <td class=title_bar>Version</td>\n
                        <td class=title_bar>Args</td>\n
                        <td class=title_bar>Masterlog</td>\n
                        <td class=title_bar>Jobs Waiting</td>\n
                        <td class=title_bar>Purpose/Notes</td></tr>\n
        ''')
    elif type == "paused":
        print('''
            <tr><td class=title_bar>Test Bed</td>\n
                        <td class=title_bar colspan=5>Reason</td>\n
                        <td class=title_bar>Jobs Waiting</td>\n
                        <td class=title_bar>Purpose/Notes</td></tr>\n
        ''')
    else:
        print("")


def  change_result_index(url, tb):
    global ip_list
    file = "/{tb}/results/index.html"
    tb_ip = ip_list[tb]
    fd = open(file, "w")
    the_content = '''
        <HTML>
            <link rel=\"shortcut icon\" href=\"http://$tb/status/images/favicon.ico\">
            <link rel=\"shortcut icon\" href=\"http://$tb_ip/status/images/favicon.ico\">
            <title>Daily Summary @ $tb</title>

            <frameset cols=\"18%,*\">
              <frame src=\"../status/result.php\" name=\"left\">
              <frame src=\"$url\" name=\"right\">
             </frameset>
           <frameset cols=\"20%,*\">
         </HTML>
    '''
    File_object = open(rf"{file}", the_content)
    File_object.close() 