# -*- coding: utf-8 -*-

import getpass
import os

# Deployment options. Overridable via the command-line
DEPLOY_HOST = 'localhost'
DEPLOY_PORT = 22
DEPLOY_USER = getpass.getuser()
DEPLOY_DIR = 'pelletron'
DEPLOY_NO_MAKE_DIR = False
DEPLOY_DELETE = False

# Search settings
SEARCH_ENABLED = True

# Test server options. Overridable via the command-line
SERVE_HOST = 'localhost'
SERVE_PORT = 5050

PELLETRON_FRAMEWORK = 'custom'
PELLETRON_ACTION = None

SECRET_KEY = None

DEBUG = True

FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

FREEZER_DESTINATION='../built'
FREEZER_REMOVE_EXTRA_FILES=False

# To see all available styles execute the following in your pelletron
# virtual directory's Python REPL:
# >>> from pygments.styles import get_all_styles
# >>> styles = list(get_all_styles())
PYGMENTS_STYLE = 'tango'

COMMENTS_ENABLED = True
COMMENTS_SHOW_BY_DEFAULT = False
COMMENTS_DISQUS_SHORTNAME = ''
