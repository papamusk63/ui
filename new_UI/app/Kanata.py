from common_func import array_manipulate, FillTestbedArray, array_Order_Number, get_available

# obtain all testbed info from regress.params
aTbs = FillTestbedArray("/usr/global/bin/regress.params")

# this strips out all beds not at this site
aTbs = array_manipulate(aTbs, "SITE", "Kanata")

# reorder the list based on lowest GATEWAY
aTbs = array_Order_Number(aTbs, "GATEWAY")

kan_agent  = get_available(aTbs)

if (kan_agent == ""):
    print("<B>No test beds are on line in Kanata.</B>")

# Redirect off to a Kanata GUI
print("<META http-equiv=REFRESH content=\"0 url=http://kan_agent/status\">")