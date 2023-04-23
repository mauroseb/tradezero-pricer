# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, request, jsonify, Response, abort

main_bp = Blueprint('main_bp', __name__)

from . import views
