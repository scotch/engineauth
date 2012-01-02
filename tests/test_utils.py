import test_base
from engineauth import utils

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


default_config = {
    'base_url': '/auth',
    'provider.facebook': {
        'location': 'engineauth.strategies.facebook',
        'client_id': None,
        'client_secret': None,
        'scope': 'email',
        },
    'provider.google': {
        'location': 'engineauth.strategies.google',
        'client_id': None,
        'client_secret': None,
        'api_key': None,
        'scope': 'https://www.googleapis.com/auth/plus.me',
        },
    }

user_config = {
    'provider.facebook': {
        'client_id': '12345',
        'client_secret': 'abcd',
        'scope': 'email, phonenumber',
        },
    'provider.google': {
        'client_id': '54321',
        'client_secret': 'dcba',
        'api_key': 'apikey',
        },
    'provider.vimeo': {
        'location': 'vimeo.strategies.vimeo',
        'client_id': 'v1234',
        'client_secret': 'vabc',
        'scope': 'email',
        },
    }

class TestLoadConfig(test_base.BaseTestCase):

    def setUp(self):
        super(TestLoadConfig, self).setUp()

    def test_load_config(self):
        c = utils.load_config(default_config, user_config)
        self.assertEqual(c['provider.facebook'], {
            'location': 'engineauth.strategies.facebook',
            'client_id': '12345',
            'client_secret': 'abcd',
            'scope': 'email, phonenumber',
            })
        self.assertEqual(c['provider.vimeo'], {
            'location': 'vimeo.strategies.vimeo',
            'client_id': 'v1234',
            'client_secret': 'vabc',
            'scope': 'email',
            })
        self.assertEqual(c['base_url'], '/auth')


class TestImportStringClass(object):
    pass

class TestImportClass(test_base.BaseTestCase):
    def test_import_class(self):
        klass = utils.import_class('test_utils.TestImportStringClass')
        self.assertEqual(klass, TestImportStringClass)
