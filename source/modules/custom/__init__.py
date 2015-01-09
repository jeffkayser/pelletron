# -*- coding: utf-8 -*-

from flask import Blueprint

MODULE_NAME = 'custom'

module = Blueprint(MODULE_NAME, __name__, url_prefix='', template_folder='/templates/{}'.format(MODULE_NAME), static_folder='/static/{}'.format(MODULE_NAME))

import view
