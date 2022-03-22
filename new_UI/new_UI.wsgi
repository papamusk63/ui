#!/tmp/new_UI_venv/bin/python

# def application(environ, start_response):
#     status = '200 OK'
#     output = b'Hello World!'

#     response_headers = [('Content-type', 'text/plain'),
#                         ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)

#     return [output]

import sys
from flask import Flask, json, request, render_template_string, jsonify
from flask.templating import render_template

template_dir = "/wfdcdev07/ws/infra/regressstatus/new_UI/app/templates"
application = Flask("new_UI",template_folder=template_dir)
sys.path.insert(0,"/var/www/html/ws/infra/regressstatus/new_UI")
sys.stdout = sys.stderr

from app import jobs_index, masterlog
from app.serverFunctions import server_methods

@application.route("/")
def index():
    return "Welcome to the Flask Index page"

@application.route("/debug")
def debug():
    print(request.__dict__)
    return jsonify(request.cookies)

@application.route("/jobs",methods=['GET','POST'])
def jobs():
    #return render_template_string(jobs_index.render(request))
    data = jobs_index.render(request)
    return render_template('jobs_index.html',data=data)

@application.route("/masterlog",methods=['GET','POST'])
def masterlog():
    data = masterlog.render(request)
    return render_template('masterlog.html',data=data)

@application.route("/xmlrpc",methods=['POST'])
def serverFunctions():
    all_funcs = server_methods
    # Assume function to be called is in request.rpcfunc
    # and args in request.rpcfunc_args
    try:
        request_body = request.get_json() #TODO - Add catch exception for all the possible errors here
    except:
        return render_template_string(all_funcs['malformed_request']()), 400
    called_func = all_funcs.get(request_body.get('rpcfunc'))
    called_func_args = request_body.get('rpcfunc_args')
    if called_func is not None:
        try:
            return jsonify(called_func(request,called_func_args))
        except Exception as excp:
            return render_template_string('Exception. Check error log.'), 500

    else:
        return render_template_string(all_funcs['method_not_found']()), 501
