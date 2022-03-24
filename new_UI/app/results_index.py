import os
from common_func import *

def results_index(request):
    myhost = request['HTTP_HOST']
    host = ('hostname -s').strip()
    # rowserver variable only exists on rowservers, serving virtual beds
    rowserver = os.getenv('ROWSERVER')

    if rowserver == host:
        #we need the virtual host name iso the rowserver
        temp = request['SERVER_NAME']
        host['domain_not_wanted'] = temp.spilte('.')

    # else we are in a non-virtual environment -- do nothing: host var is ok as is
    aTb = FillTestbedArray("/usr/global/bin/regress.params")
    host_ip = aTb[host]['IP']
    if host_ip:
        host_ip = host
    
    # get what was requested, note that this is called through http.conf where anyone that
    # happens to be in the "day" directory will be diverted to here. It cannot be called, nor
    # will work from anywhere else but the day directory.
    location = os.getenv('REQUEST_URI')
    # $iStart = strpos($location, "20");
    # $location = substr($location, $iStart);

    print("<META http-equiv=REFRESH content=\"0; url=http://$myhost/status/livesearch.php?q=$location\">")