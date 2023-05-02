# -*- coding: utf-8 -*-

import json
import socket
import time

from flask import render_template, Blueprint, current_app, jsonify,\
    Response, abort
from flasgger import swag_from
from . import main_bp



def check_backend():
    # check mongo and yf
    return "success"

@main_bp.route("/index", methods=['GET', 'POST'])
@main_bp.route("/", methods=['GET', 'POST'])
def main():
    tzp_version = current_app.config['TZP_VERSION']
    tzp_commit = current_app.config['TZP_VERSION_COMMIT']
    return render_template('base.html', tzp_version=tzp_version, tzp_commit=tzp_commit)

@main_bp.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@main_bp.route("/docs", methods=['GET', 'POST'])
def docs():
    return render_template('apidocs.html')

@main_bp.route('/health')
@swag_from("health.yml")
def healthcheck():
    '''
    Service healthcheck endpoint
    '''
    status = check_backend()
    status_code = 200 if status == "success" else 500

    data = {
        'hostname': socket.gethostname(),
        'code': status_code,
        'status': status,
        'timestamp': time.time(),
        #'results': results,
    }

    response = Response(json.dumps(data), status=status_code, mimetype='application/json')

    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'

    return response


@main_bp.route("/version")
@swag_from("version.yml")
def version():
    '''
    Return version
    '''
    tzp_version = current_app.config['TZP_VERSION']
    tzp_commit = current_app.config['TZP_VERSION_COMMIT']
    fullversion = tzp_version.split('.')
    data = {
        'result': 200,
        'version': tzp_version,
        'major': fullversion[0],
        'minor': fullversion[1],
        'release': fullversion[2],
        'commit': tzp_commit,
        'api': 'v1',
    }
    return Response(json.dumps(data), mimetype='application/json')

