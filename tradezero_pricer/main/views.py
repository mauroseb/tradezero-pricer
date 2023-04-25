# -*- coding: utf-8 -*-

import json
import socket
import time

from flask import render_template, Blueprint, current_app, jsonify,\
    Response, abort
from flasgger import swag_from
from . import main_bp

tzp_major = 0
tzp_minor = 1
tzp_release = 4
tzp_version = f'{tzp_major}.{tzp_minor}.{tzp_release}'
#tzp_version = app.config['TZP_VERSION']
tzp_commit = '8389e6144fb74ef0a3652c35a31860fe'


def check_backend():
    # check mongo and yf
    return "success"

@main_bp.route("/index", methods=['GET', 'POST'])
@main_bp.route("/", methods=['GET', 'POST'])
def main():
    return render_template('base.html')

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
    """Return version"""
    data = {
        'result': 200,
        'version': tzp_version,
        'major': tzp_major,
        'minor': tzp_minor,
        'release': tzp_release,
        'commit': tzp_commit,
        'api': 'v1',
    }
    return Response(json.dumps(data), mimetype='application/json')

