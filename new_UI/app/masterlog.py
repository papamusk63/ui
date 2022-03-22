from itertools import count
import os
from platform import version
import re
import socket
from collections import OrderedDict
from glob import glob
from urllib.parse import unquote

from sre_constants import AT
from pprint import pprint
from jinja2 import Template
from flask import request as FlaskRequest

from .common_func import *
from .read_masterlog2 import *
from .time_left import *
from .globals import *


def render(request: FlaskRequest):
    
    template_fill = {}
    myhost = request.host
    host = socket.gethostbyname()

    aTb = FillTestbedArray("/usr/global/bin/regress.params")
    host_ip = aTb[host].get('IP',socket.getfqdn())

    running_ip = host_ip

    note = htmlspecialchars(aTb[host]['DESCRIPTION'])

    del aTb

    sim_logs = dict()
    id = 0

    js_loc = "http://$myhost/status/masterlog/js/masterlog.js"
    css_loc = "http://$myhost/status/masterlog/css/masterlog.css"
    img_loc = "http://$myhost/status/masterlog/"
    
    location: str = request.environ.get('REQUEST_URI')

    loc_parts = location.split(sep = '\/')
    test_dir = f"/{host}{loc_parts[0]}/{loc_parts[1]}/{loc_parts[2]}/{loc_parts[3]}/{loc_parts[4]}/{loc_parts[5]}/"
    path = f"{loc_parts[0]}/{loc_parts[1]}/{loc_parts[2]}/{loc_parts[3]}/{loc_parts[4]}/{loc_parts[5]}/"
    results_index = f"/{host}{loc_parts[0]}/{loc_parts[1]}/{loc_parts[2]}/{loc_parts[3]}/{loc_parts[4]}/"
    test_dir_url = f"http://{myhost}{loc_parts[0]}/{loc_parts[1]}/{loc_parts[2]}/{loc_parts[3]}/{loc_parts[4]}/{loc_parts[5]}/"

    template_fill['loc_parts'] = loc_parts
    template_fill['test_dir'] = test_dir
    template_fill['path'] = path
    template_fill['results_index'] = results_index
    template_fill['test_dir_url'] = test_dir_url

    # do we have a sub test cookie set?
    sGroup = "All"
    bSubTest = 1
    if request.cookies.get('SrGuiSubTest') is not None:
        sSelectCookie = request.cookies['SrGuiSubTest']
        if sSelectCookie:
            aInfo = sSelectCookie.split(" ")
            bSubTest = aInfo[0]
    
    os.chdir(test_dir)

    # ---- #
    # MAIN #
    # ---- #
    d_array = []
    for d in os.listdir():
        if os.path.isfile(d):
            d_array.append(d)
    
    global aTestSuite
    global aTestCase
    global aSubTest

    if os.path.exists(f"{test_dir}/intendedTestList") and os.path.isfile(f"{test_dir}/intendedTestList"):
        for filename in d_array:
            if re.match('(ESR|WMM)\.([^.]+)\.(.*)\.(html|txt)',filename):
                matches = re.match('(ESR|WMM)\.([^.]+)\.(.*)\.(html|txt)',filename).groups()
                if matches[1] in sim_logs and \
                    matches[2] in sim_logs[matches[1]] and \
                        matches[3] in sim_logs[matches[1]][matches[2]]:
                        sim_logs[matches[1]][matches[2]][matches[3]] += 1
                else:
                    sim_logs[matches[1]][matches[2]][matches[3]] = 1
            
            if filename == 'masterlog.txt':
                getRunInfo(host,path,"detail")
            if filename == 'version.txt':
                version = get_file_content(f"{test_dir}/{filename}")
            if filename == 'args':
                get_args = get_file_content(f"{test_dir}/{filename}")
    
    #do we have notes
    noteList = glob(f"/{host}/jobs/note_*")
    myNoteCount = count(noteList)
    icon = ""
    if myNoteCount==1:
        icon = f"http://{myhost}/status/images/sticky-note-pin_single.png"
    elif myNoteCount>1:
        icon = f"http://{myhost}/status/images/sticky-note-pin_double.png"

    template_fill['icon'] = icon

    sim_logs = natksort(sim_logs)
    for product, nodes in sim_logs.items():
        

    
    
    return template_fill