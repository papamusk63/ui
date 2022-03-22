from common_func import FillTestbedArray, array_manipulate, array_Order_Number, get_available

# obtain all testbed info from regress.params
aTbs = FillTestbedArray("/usr/global/bin/regress.params")

# this strips out all beds not at this site
aTbs = array_manipulate(aTbs, "SITE", "Naperville")

# reorder the list based on lowest GATEWAY
aTbs = array_Order_Number(aTbs, "GATEWAY")

nap_agent  = get_available(aTbs)

if (nap_agent == ""):
    print("<B>No test beds are on line in Naperville.</B>")
    

# Redirect off to a Naperville GUI
print("<META http-equiv=REFRESH content=\"0 url=http://nap_agent/status\">")