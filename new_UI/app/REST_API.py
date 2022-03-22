import requests

#TODO - This is a generic name being used for replacing RPC requests. Better name would be MAKE_XMLRPC_API_CALL()
#TODO 2 - Add error catching in this function
def MAKE_API_CALL(*args)-> Dict:
    server = args[0]
    #TODO - Not sure where serverLocation is used, To be used later
    serverLocation = args[1]
    rpcfunc = args[2]
    rpcfunc_args = args[3:]
    r = requests.post(url=server+serverLocation,
                    data={'rpcfunc':rpcfunc,
                    'rpcfunc_args':rpcfunc_args}
                    )
    return r.json()
