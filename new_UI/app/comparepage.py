import re

def comparepage(request):
    host = ('hostname -s').strip()
    home = ('echo HOME').strip()
    if request.method == 'POST':
        testDir = request['version']
    loc_parts = re.search('/\//', testDir)
    path = f"/{loc_parts[2]}/{loc_parts[3]}/{loc_parts[4]}/{loc_parts[5]}/{loc_parts[6]}/"

    print(f"{home}/compareWithRegressDbResults.py/{host}/{path}<br/> ")
    print("<table>")

    print("<b>More detailed results from RegressDb coming up: </b><br/><br/>")
    print("</table>")
