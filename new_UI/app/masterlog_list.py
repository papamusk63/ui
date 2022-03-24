import os
from common_func import *

aTb = FillTestbedArray("/usr/global/bin/regress.params")


test_dir = "/hostloc_parts[0]/loc_parts[1]/loc_parts[2]/loc_parts[3]/loc_parts[4]/loc_parts[5]/"
test_dir_url = "http://myhostloc_parts[0]/loc_parts[1]/$loc_parts[2]/$loc_parts[3]/$loc_parts[4]/$loc_parts[5]"

def masterlog_list(request):
    myhost = request['HTTP_HOST']
    host = ('hostname -s').strip()
    # rowserver variable only exists on rowservers, serving virtual beds
    rowserver = os.getenv('ROWSERVER')
    if rowserver == host:
        #we need the virtual host name iso the rowserver
        temp = request['SERVER_NAME']
        host['domain_not_wanted'] = temp.splite('.')
    

    host_ip = aTb[host]['IP']
    if host_ip is None:
        host_ip = host
    
    img_loc = f"http://{myhost}/status/masterlog/"
    location = os.getenv('REQUEST_URI')
    loc_parts = re.search('/\//', location)


    print('''
        "<html><head>\n";
        "<META HTTP-EQUIV=\"Cache-Control\" CONTENT=\"no-cache\">\n";
        "<META HTTP-EQUIV=\"Pragma\" CONTENT=\"no-cache\">\n";
        "<META HTTP-EQUIV=\"Expires\" CONTENT=\"-1\">\n";
    ''')

    # definition for the favicon
    print("<link rel=\"shortcut icon\" href=\"http://$host/status/images/favicon.ico\">\n")
    print("<link rel=\"stylesheet\" type=\"text/css\" href=\"http://$myhost/status/css/test.css\">\n")

    title = f"{[host]:}.{loc_parts[4]}._{loc_parts[2]}./.{loc_parts[5]}"
    title2 = f"{[host]:}.{loc_parts[4]}.<BR>{loc_parts[2]}./.{loc_parts[5]}"
    print(f"<title>{title}</title>\n")
    print("</head><body>\n")

    tree_file = "/host/status/tree_nodes2.js"
    tree_format = "/host/status/tree_format2.js"

    file_d = open(tree_file, "w")
    file_d.write("var TREE1_FORMAT = [\n")
    file_d.write("15,\n")
    file_d.write("15,\n")
    file_d.write("true,\n")
    file_d.write("[\"http://$myhost/status/images/collapsed_button.gif\", \"http://$myhost/status/images/expanded_button.gif\", \"http://$myhost/status/images/blank.gif\"],\n")
    file_d.write("[16,16,0],\n")
    file_d.write("true,\n")
    file_d.write("[\"http://$myhost/status/images/closed_folder.gif\", \"http://$myhost/status/images/opened_folder.gif\", \"http://$myhost/status/images/document.gif\"],\n")
    file_d.write("[16,16],\n")
    file_d.write("[0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,256,272],\n")
    file_d.write("\"\",\n")
    file_d.write("\"clsNode\",\n")
    file_d.write("true,\n")
    file_d.write("[1,0],\n];")
    file_d.close

    print("<script language=\"JavaScript\" src=\"http://$myhost/status/tree_nodes2.js\"></script>\n")
    print("<script language=\"JavaScript\" src=\"http://$myhost/status/tree_format2.js\"></script>\n")

    print('''
        <div name=\"right\"> </div>
        <script type=\"text/javascript\">
      var tree = new COOLjsTree(\"tree1\", TREE1_NODES, TREE1_FORMAT);\n"


      tree.expandNode(0);
      tree.draw();\n";

      </script></body>\n

    ''')

def listdir(start_dir, file_d, flag):
    global test_dir_url
    global paths
    files = {}
    dirs = {}

    fh = open(start_dir)
    dirs = fh
    for dirName in fh:
        filepath = start_dir + '/' + dirName
        open(file_d, "\t\t['dirName', null, null,\n")
        listdir(filepath, file_d, 1)
        
    fh = open(start_dir)
    dirs = fh
    for dirName in fh:
        filepath = start_dir + '/' + dirName
        open(file_d, "\t\t['dirName', null, null,\n")
        listdir(filepath, file_d, 1)
