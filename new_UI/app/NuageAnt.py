from common_func import *
from common_func import array_manipulate, array_Order_Number, get_available

# obtain all testbed info from regress.params
aTbs = FillTestbedArray("/usr/global/bin/regress.params")

# this strips out all beds not at this site
aTbs = array_manipulate(aTbs, "SITE", "NuageAnt")

# reorder the list based on lowest GATEWAY
aTbs = array_Order_Number(aTbs, "GATEWAY")

nuage_ant_agent = get_available(aTbs)

if nuage_ant_agent == "":
    print("<B>No test beds are on line in NuageAnt.</B>")

# Redirect off to a NuageAnt GUI
print("<META http-equiv=REFRESH content=\"0; url=http://$nuage_ant_agent/status\">")