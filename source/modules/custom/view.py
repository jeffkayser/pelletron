# -*- coding: utf-8 -*-

# Add any default Pelletron-only view logic here as follows:
#
# @module.route('/path/')
# def path():
#     return render_template('template.html')

from flask import render_template

from source import app

from . import module

@module.route('/')
def index():
    return render_template('{}/index.html'.format(app['PELLETRON_FRAMEWORK']))
