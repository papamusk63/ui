from common_func import *

def genericSite(request):
    site = request['site']
    # obtain all testbed info from regress.params
    aTbs = FillTestbedArray("/usr/global/bin/regress.params", site)

    # reorder the list based on lowest GATEWAY
    aTbs = array_Order_Number(aTbs, "GATEWAY")

    agent  = get_available(aTbs)

    if agent == "":
        print(f"<B>No test beds are on line in {site}.</B>")
    
    print(f"<META http-equiv=REFRESH content=\"0; url=http://{agent}/status\">")