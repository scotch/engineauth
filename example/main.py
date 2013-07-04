# -*- coding: utf-8 -*-
import sys
import os
import re
import webapp2
from webapp2 import Route
import os
from jinja2.filters import do_pprint

if 'lib' not in sys.path:
    sys.path[0:0] = ['lib']

DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

routes = [
    Route(r'/', handler='handlers.PageHandler:root', name='pages-root'),

    # Wipe DS
    Route(r'/tasks/wipe-ds', handler='handlers.WipeDSHandler', name='wipe-ds'),
    ]

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    },
    'webapp2_extras.jinja2': {
        'filters': {
            'do_pprint': do_pprint,
            },
        },
    }


application = webapp2.WSGIApplication(routes, debug=DEBUG, config=config)
