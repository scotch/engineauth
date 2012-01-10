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
    Route(r'/tasks/whip-ds', handler='handlers.WipeDSHandler', name='whip-ds'),

    # Account Settings
    Route(r'/settings', handler='handlers.AccountIndexHandler', name='account-index'),
    Route(r'/settings/email', handler='handlers.AccountEmailHandler', name='account-email'),
    Route(r'/settings/password', handler='handlers.AccountPasswordHandler', name='account-password'),
    # Password
    Route(r'/password/reset', handler='handlers.PasswordResetHandler', name='password-reset'),
    Route(r'/password/reset/<token>', handler='handlers.PasswordResetCompleteHandler', name='password-reset-check'),
    ]

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    },
    'webapp2_extras.auth': {
        #        'user_model': 'models.User',
        'user_attributes': ['displayName', 'email'],
        },
    'webapp2_extras.jinja2': {
        'filters': {
            'do_pprint': do_pprint,
            },
        },
    }


application = webapp2.WSGIApplication(routes, debug=DEBUG, config=config)
