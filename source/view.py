# -*- coding: utf-8 -*-

import os

from flask import abort, render_template, render_template_string, request, send_from_directory, url_for
from jinja2 import TemplateNotFound

from source import app, controller as c, model as m, pages
from flask_flatpages import pygments_style_defs

framework = app.config['PELLETRON_FRAMEWORK']

@app.route('/')
def index():
    return quickstart()   # TODO: Delete this line
    return page('home')

# TODO: Delete this function
@app.route('/quickstart')
def quickstart():
    return render_template('{}/quickstart.html'.format(framework))

@app.route('/<path:page>/')
@app.route('/<path:page>')
def page(page):
    #try:
        page = pages.get_or_404(page)
        template = page.meta.get('template', 'page.html')
        template = '{}/{}'.format(framework, template)
        print 'page ' + template
        return render_template(template, page=page)
    #except TemplateNotFound:
    #    abort(404)

@app.route('/css/pygments.css')
def pygments_css():
    return pygments_style_defs(app.config['PYGMENTS_STYLE']), 200, {'Content-Type': 'text/css'}

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def error_page_not_found(error):
    return render_template('error-404.html'), 404
