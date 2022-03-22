from .common_func import FillTestbedArray, array_manipulate, array_Order_Number, get_available

# obtain all testbed info from regress.params
aTbs = FillTestbedArray("/usr/global/bin/regress.params")

# this strips out all beds not at this site
aTbs = array_manipulate(aTbs, "SITE", "Bratislava")

# reorder the list based on lowest GATEWAY
aTbs = array_Order_Number(aTbs, "GATEWAY")

brat_agent  = get_available(aTbs)

if brat_agent == "":
    print("<B>No test beds are on line in Bratislava.</B>")

print(f'<META http-equiv=REFRESH content=\"0; url=http://{brat_agent}/status\"')