from engineauth.middleware import AuthMiddleware
from engineauth.middleware import EngineAuthRequest
from engineauth import models
import test_base
import webapp2
import ndb
import engineauth.config

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class CustomUser(models.User):
    custom_property = ndb.StringProperty(default='yep')

    @classmethod
    def _get_kind(cls):
        return 'CustomUser'

default_config1 = {
    'base_uri': '/custom-base',
    'login_uri': '/custom-login',
    'success_uri': '/',
    'secret_key': 'CHANGE_TO_A_SECRET_KEY', # We add this here for testing only
    'user_model': 'tests.test_config.CustomUser',
    'provider.facebook': {
        'class_path': 'engineauth.strategies.facebook.FacebookStrategy',
        'client_id': None,
        'client_secret': None,
        'scope': 'email',
        },
    }

app1 = AuthMiddleware(webapp2.WSGIApplication(), config=default_config1)


class TestConfig(test_base.BaseTestCase):
    def setUp(self):
        super(TestConfig, self).setUp()

    def test_load_config(self):
        c1 = engineauth.config.load_config()
        self.assertEqual(c1['base_uri'], '/auth')
        self.assertEqual(c1['login_uri'], '/login')

        c2 = engineauth.config.load_config(default_config1)
        self.assertEqual(c2['base_uri'], '/custom-base')
        self.assertEqual(c2['login_uri'], '/custom-login')
        self.assertEqual(c2['user_model'], 'tests.test_config.CustomUser')

    def test__load_user_custom_user_model(self):
        # Test without custom User
        user = models.User.create_user('test:12345')
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()
        req.session.user_id = user.get_id()
        req._load_user()
        self.assertEqual(user, req.user)

        # Now custom User
        user = CustomUser.create_user('test:12345')
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()
        req.session.user_id = user.get_id()
        req._load_user()
        self.assertEqual(req.user, user)
        self.assertEqual(req.user.custom_property, 'yep')
        self.assertEqual(req.user.__class__, CustomUser.__class__)

