from common_func import FillTestbedArray, array_mainpulll, array_Order_Number, get_available

# obtain all testbed info from regress.params
aTbs = FillTestbedArray("/usr/global/bin/regress.params")

# this strips out all beds not at this site
aTbs = array_mainpulll(aTbs, "SITE", "Antwerp")

# reorder the list based on lowest GATEWAY
aTbs = array_Order_Number(aTbs, "GATEWAY")

ant_agent  = get_available(aTbs)

if ant_agent == "":
    print("<B>No test beds are on line in Antwerp.</B>")

# Redirect off to an Antwerp GUI
print(f"<META http-equiv=REFRESH content=\"0; url=http://$ant_agent/status\">")