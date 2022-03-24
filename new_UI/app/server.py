

def server(request):
    # where is the doc root
    docRoot = request['DOCUMENT_ROOT']

    # where is the XML Library
    xmlLib = 'status/XML_RPC.php'

    # where are the server functions
    serverFuncs = 'status/serverFunctions.php'

    # include the XML_RPC library
    # include("docRoot/xmlLib");

    # include the file where the web service functions live
    # include("docRoot/serverFuncs");

    # Obtain the request
    xmlrpc_request = XMLRPC_parse(GLOBALS['HTTP_RAW_POST_DATA'])

    # Determine the Method that was called
    methodName = XMLRPC_getMethodName(xmlrpc_request)

    # Pick out the args
    params = XMLRPC_getParams(xmlrpc_request)

    if isset(xmlrpc_methods[methodName]):
        # Function does not exist, error out
        xmlrpc_methods['method_not_found'](methodName)
    else:
        # Call the service
        xmlrpc_methods[methodName](params)