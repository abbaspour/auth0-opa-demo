#!/usr/bin/env python

# from: https://github.com/open-policy-agent/contrib/blob/master/api_authz/docker/echo_server.py
import base64
import os

from flask import Flask
from flask import request
import json
import requests

import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

app = Flask(__name__)

opa_url = os.environ.get("OPA_ADDR", "http://localhost:8181")
policy_path = os.environ.get("POLICY_PATH", "/v1/data/httpapi/authz")

def check_auth(url, method, url_as_array, access_token):
    input_dict = {"input": {
        "access_token": access_token,
        "path": url_as_array,
        "method": method,
    }}

    logging.info("Checking auth...")
    logging.info(json.dumps(input_dict, indent=2))
    try:
        rsp = requests.post(url, data=json.dumps(input_dict))
    except Exception as err:
        logging.info(err)
        return {}
    j = rsp.json()
    if rsp.status_code >= 300:
        logging.info("Error checking auth, got status %s and message: %s" % (j.status_code, j.text))
        return {}
    logging.info("Auth response:")
    logging.info(json.dumps(j, indent=2))
    return j

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    authz_header = request.headers.get('Authorization')
    access_token = authz_header.split("Bearer ")[1]
    url = opa_url + policy_path
    path_as_array = path.split("/")
    j = check_auth(url, request.method, path_as_array, access_token).get("result", {})
    if j.get("allow", False) == True:
        return "Success: user is authorized \n"
    return "Error: user is not authorized to %s url /%s \n" % (request.method, path)

if __name__ == "__main__":
    app.run()
