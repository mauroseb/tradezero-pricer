# -*- coding: utf-8 -*-

import os

from flask import Flask, request, jsonify, Response, abort, render_template
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flasgger import Swagger
from datetime import date
from tradezero_pricer.config import config as tzp_config

bootstrap = Bootstrap()
db = MongoEngine()

def create_app(config_name):
    '''
    Application Factory
    '''
    app = Flask(__name__)
    app.config.from_object(tzp_config.config[config_name])
    tzp_config.config[config_name].init_app(app)
    cors = CORS(app)
    swagger = Swagger(app)
    db.init_app(app)
    bootstrap.init_app(app)
    add_error_handlers(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from tradezero_pricer.main import main_bp
    #app.register_blueprint(main_bp, url_prefix='/', template_folder='templates', static_folder='assets' )
    app.register_blueprint(main_bp, url_prefix='/', template_folder='templates' )

    from tradezero_pricer.api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    app.logger.info("TradeZero Pricer running.")

    return app


def add_error_handlers(app):
    '''
    Register Error Handlers
    '''
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

