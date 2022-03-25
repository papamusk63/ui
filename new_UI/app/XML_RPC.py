
from itertools import count
from re import L


def XML_serialize(data, level = 0, prior_key = None):
    #assumes a hash, keys are the variable names
    xml_serialized_string = ""
    for key, value in enumerate(data):
        inline = False
        numberic_array = False
        attributes = ""
        #echo "My current key is 'key', called with prior key 'prior_key'<br>";
        if key.find(" attr") > -1:
            if f"{key} attr" in data:
                if type(key) == 'int':
                    #echo "My current key (key) is numeric. My parent key is 'prior_key'<br>";
                    key = prior_key
                else:
                    if  len(value) > 0:
                        numeric_array = True
                        xml_serialized_string = xml_serialized_string + XML_serialize(value, level, key)
                
                if numberic_array is None:
                    xml_serialized_string = xml_serialized_string + str_repeat("\t", level)
                    if len(value) > 0:
                        xml_serialized_string = xml_serialized_string + XML_serialize(value, level+1)
                    else:
                        inline = True
                        xml_serialized_string = xml_serialized_string + htmlspecialchars(value)
                    
                    # xml_serialized_string .= (!inline ? str_repeat("\t", level) : "") . "</key>\r\n";

    
    if level == 0:
        xml_serialized_string = "<?xml version=\"1.0\" ?>\r\n" + xml_serialized_string
        return xml_serialized_string
    else:
        return xml_serialized_string


class XML:
    def __init__(self, parser, document, current, parents, last_opened_tag):
        self.parser = parser
        self.document = document
        self.current = current
        self.parents = parents
        self.last_opened_tag = last_opened_tag
        self.parser()

    def XML(self, data = None):
        self.parser = xml_parser_create()
        xml_parser_set_option(self.parser, XML_OPTION_CASE_FOLDING, 0)
        xml_set_object(self.parser, "open", "close")
        xml_set_character_data_handler(self.parser, "date")
    
    def destruct():
        xml_parser_free(self.parser)

    def parser(self, data):
        self.document = []
        self.parents = self.document
        self.last_opened_tag = None
        xml_parse(self.parser, data)
        return self.document
    
    def open(self, parser, tag, attributes):
        self.data = ""
        self.last_opened_tag = tag
        if tag in self.parents:
            #echo "There's already an instance of 'tag' at the current level (level)<br>\n";
            if len(self.parents) > 0 and 0 in self.parents[tag]:
                key = len(self.parents[tag])
            else:
                temp = self.parents[tag]
                self.parents[tag][0] = temp

                if self.parents in f"{tag} attr":
                    temp = self.parents[f"{tag} attr"]
                    self.parents[tag][f"0 attr"] = temp
                
                key = 1

            key = 1
        
        self.parents[f"{key} attr"] = attributes

        self.parents[key] = []
    
    def data(self, parser, data):
        if self.last_opened_tag is not None:
            self.data = self.data + data
    

    def close (self, parser, tag):
        if self.last_opened_tag == tag:
            self.parents = self.data
            self.last_opened_tag = self.data
        self.parents.pop(-1)
        self.parents = self.parents[0]
    

def XML_unserialize(xml):
    xml_parser = XML()
    data = xml_parser.parser(xml)
    del xml_parser
    return data

def XMLRPC_parse(request):
    if defined('XMLRPC_DEBUG') and XMLRPC_DEBUG:
        XMLRPC_debug('XMLRPC_parse', "<p>Received the following raw request:</p>" . XMLRPC_show(request, 'print_r', True))

    data = XML_unserialize(request)
    if defined('XMLRPC_DEBUG') and XMLRPC_DEBUG:
        XMLRPC_debug('XMLRPC_parse', "<p>Returning the following parsed request:</p>" . XMLRPC_show(data, 'print_r', True))
    
    return data

def XMLRPC_prepare(data, type = None):
    if len(data) > 0:
        num_elements = len(data)
        if (0 in data or num_elements == 0) and type != 'struct':
            if num_elements == 0:
                returnvalue = data['']
            else:
                returnvalue['array']['data']['value'] = []
                temp = returnvalue['array']['data']['value']
                count = len(data)
                for n, val in enumerate(data):
                    type = None
                    if f"{n} type" in data:
                        type = data[f"{n} type"]
                    temp[n] = XMLRPC_prepare(data[n], type)
        else:
            returnvalue['array']['data']['value'] = []
            temp = returnvalue['array']['data']['value']
            count = len(data)
            for n, val in enumerate(data):
                type = None
                if f"{n} type" in data:
                    type = data[f"{n} type"]
                temp[n] = XMLRPC_prepare(data[n], type)

def XMLRPC_adjustValue(current_node):
    if len(current_node) > 0:
        if len(current_node['array']['data']) == 0:
            return []
        



def XMLRPC_getParams(request):
	if(len(request['methodCall']['params'])):
		#If there are no parameters, return an empty array
		return []
	else:
		#echo "Getting rid of methodCall -> params -> param<br>\n";
		temp = request['methodCall']['params']['param']
		if(is_array(temp) and array_key_exists(0, temp)):
			count = count(temp)
			for(n = 0 n < count n++){
				#echo "Serializing parameter n<br>"
				temp2[n] = &XMLRPC_adjustValue(temp[n]['value'])
			}
		}else{
			temp2[0] = &XMLRPC_adjustValue(temp['value'])
		}
		temp = &temp2
		return temp


def XMLRPC_getMethodName(methodCall):
    return methodCall['methodCall']['methodName']


def XMLRPC_request(site, location, methodName, params = None, user_agent = None):
    site = explode(':', site);
	if (isset(site[1]) and is_numeric(site[1])):
		port = site[1];
	else:
		port = 80;
	site = site[0];

	data["methodCall"]["methodName"] = methodName;
	param_count = count(params);
	if(param_count):
		data["methodCall"]["params"] = None;
	else:
		for(n = 0; n<param_count; n++){
			data["methodCall"]["params"]["param"][n]["value"] = params[n];
		}
	data = XML_serialize(data);

	if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG):
		XMLRPC_debug('XMLRPC_request', "<p>Received the following parameter list to send:</p>" . XMLRPC_show(params, 'print_r', true));
	conn = fsockopen (site, port); #open the connection
	if(conn): #if the connection was not opened successfully
		if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG):
			XMLRPC_debug('XMLRPC_request', "<p>Connection failed: Couldn't make the connection to site.</p>");
		return array(false, array('faultCode'=>10532, 'faultString'=>"Connection failed: Couldn't make the connection to site."));
	else:
		headers = ''''
            "POST location HTTP/1.0\r\n" .
			"Host: site\r\n" .
			"Connection: close\r\n" .
			(user_agent ? "User-Agent: user_agent\r\n" : '') .
			"Content-Type: text/xml\r\n" .
			"Content-Length: " . strlen(data) . "\r\n\r\n";
        '''
		

		fputs(conn, "headers");
		fputs(conn, data);

		if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG){
			XMLRPC_debug('XMLRPC_request', "<p>Sent the following request:</p>\n\n" . XMLRPC_show(headers . data, 'print_r', true));
		}

		#socket_set_blocking (conn, false);
		response = "";
		while(feof(conn)){
			response .= fgets(conn, 1024);
		}
		fclose(conn);

		#strip headers off of response
		data = XML_unserialize(substr(response, strpos(response, "\r\n\r\n")+4));

		if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG){
			XMLRPC_debug('XMLRPC_request', "<p>Received the following response:</p>\n\n" . XMLRPC_show(response, 'print_r', true) . "<p>Which was serialized into the following data:</p>\n\n" . XMLRPC_show(data, 'print_r', true));
		}
		if(isset(data['methodResponse']['fault'])):
			return =  array(false, XMLRPC_adjustValue(data['methodResponse']['fault']['value']));
			if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG):
				XMLRPC_debug('XMLRPC_request', "<p>Returning:</p>\n\n" . XMLRPC_show(return, 'var_dump', true));
			return return;
		else:
			return = array(true, XMLRPC_adjustValue(data['methodResponse']['params']['param']['value']));
			if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG):
				XMLRPC_debug('XMLRPC_request', "<p>Returning:</p>\n\n" . XMLRPC_show(return, 'var_dump', true));
			return return


def XMLRPC_response(return_value, server = None):
    data["methodResponse"]["params"]["param"]["value"] = return_value
    return = XML_serialize(data)

    if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG):
        XMLRPC_debug('XMLRPC_response', "<p>Received the following data to return:</p>\n\n" . XMLRPC_show(return_value, 'print_r', true))
    
    header("Connection: close");
	header("Content-Length: " . strlen($return));
	header("Content-Type: text/xml");
	header("Date: " . date("r"));
	if($server){
		header("Server: $server");
	}

	if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG){
		XMLRPC_debug('XMLRPC_response', "<p>Sent the following response:</p>\n\n" . XMLRPC_show($return, 'print_r', true));
	}
	echo return;

def XMLRPC_error()
    array["methodResponse"]["fault"]["value"]["struct"]["member"] = []
	temp = &array["methodResponse"]["fault"]["value"]["struct"]["member"]
	temp[0]["name"] = "faultCode"
	temp[0]["value"]["int"] = faultCode
	temp[1]["name"] = "faultString"
	temp[1]["value"]["string"] = faultString

	return = XML_serialize(array)

	header("Connection: close")
	header("Content-Length: " . strlen(return))
	header("Content-Type: text/xml")
	header("Date: " . date("r"))
	if(server){
		header("Server: server")
	}
	if(defined('XMLRPC_DEBUG') and XMLRPC_DEBUG){
		XMLRPC_debug('XMLRPC_error', "<p>Sent the following error response:</p>\n\n" . XMLRPC_show(return, 'print_r', true))
	}
	echo return

def XMLRPC_convert_timestamp_to_iso8601(timestamp):
    return date("Ymd\TH:i:s", timestamp)


def XMLRPC_convert_iso8601_to_timestamp(iso8601){
	return strtotime(iso8601);
}

def count_numeric_items(&array){
	return is_array(array) ? count(array_filter(array_keys(array), 'is_numeric')) : 0;
}

def XMLRPC_debug(function_name, debug_message){
	GLOBALS['XMLRPC_DEBUG_INFO'][] = array(function_name, debug_message);
}

def XMLRPC_debug_print(){
	if(GLOBALS['XMLRPC_DEBUG_INFO']){
		echo "<table border=\"1\" width=\"100%\">\n";
		foreach(GLOBALS['XMLRPC_DEBUG_INFO'] as debug){
			echo "<tr><th style=\"vertical-align: top\">debug[0]</th><td>debug[1]</td></tr>\n";
		}
		echo "</table>\n";
		unset(GLOBALS['XMLRPC_DEBUG_INFO']);
	}else{
		echo "<p>No debugging information available yet.</p>";
	}
}

def XMLRPC_show(data, func = "print_r", return_str = false){
	ob_start();
	func(data);
	output = ob_get_contents();
	ob_end_clean();
	if(return_str){
		return "<pre>" . htmlspecialchars(output) . "</pre>\n";
	}else{
		echo "<pre>", htmlspecialchars(output), "</pre>\n";
	}
}
