from unittest import result


def print_nav (host, latest, caller):
    if caller == "job_index":
        job_string = "<font size=4px>Jobs</font>"
    else:
        job_string = f"<a href=http://{host}/jobs/ title=\"Jobs\">Jobs</a>"
    
    if caller == 'results_index':
        result_string = "<font size=4px>Results</font>"
    else:
        result_string = f"<a href=http://{host}/results/>Results</a>"
    
    print('''
        <table border=1><tr>
		<td class=content_center width=33%><a href=http://$host/status/ title=\"Status Page\">Status</a></td>
		<td class=content_center width=33%>$job_string</td>
		<td class=content_center width=33%>$result_string</td>
		</tr></table>
    ''')
