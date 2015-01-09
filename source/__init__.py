# -*- coding: utf-8 -*-

from flask import Flask
from flask_flatpages import FlatPages
from flask_debugtoolbar import DebugToolbarExtension

# Initialize and configure Flask application
app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('framework')

# Initialize FlatPages extension
pages = FlatPages(app)

# Load Pelletron modules as required
framework =  app.config['PELLETRON_FRAMEWORK']
if framework == 'bootstrap':
    print("[MODULE] Using Bootstrap")
    from source.modules.bootstrap import module as bootstrap
    app.register_blueprint(bootstrap)
elif framework == 'foundation':
    print("[MODULE] Using Foundation")
    from source.modules.foundation import module as foundation
    app.register_blueprint(foundation)
elif framework == 'html5boilerplate':
    print("[MODULE] Using HTML5 Boilerplate")
    from source.modules.html5boilerplate import module as h5bp
    app.register_blueprint(h5bp)

# Load MVC stack
from source import model
from source import controller
from source import view

# Initialize debug toolbar if required
if app.config['PELLETRON_ACTION'] == 'serve':
    DebugToolbarExtension(app)
