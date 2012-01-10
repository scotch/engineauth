from engineauth.middleware import AuthMiddleware
from engineauth.middleware import EngineAuthRequest
from engineauth import models
import test_base
import webapp2

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'



app = AuthMiddleware(webapp2.WSGIApplication())

class TestAuthMiddleware(test_base.BaseTestCase):
    def setUp(self):
        super(TestAuthMiddleware, self).setUp()

    #    def test_load_config(self):
    #        req = EngineAuthRequest.blank('/auth/google')
    #        resp = req.get_response(app)
    #        self.assertEqual(resp, '/auth')

    def test_load_strategy(self):
        from engineauth.strategies.google import GoogleStrategy

        strategy_class = app._load_strategy('google')
        self.assertEqual(strategy_class, GoogleStrategy)
        self.assertRaises(Exception, app._load_strategy, 'enron')
        from engineauth.strategies.appengine_openid import\
            AppEngineOpenIDStrategy
        strategy_class = app._load_strategy('appengine_openid')
        self.assertEqual(strategy_class, AppEngineOpenIDStrategy)

    def test_load_session_no_session(self):
        req = EngineAuthRequest.blank('/auth/google')
        # No Session
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 0)
        sess = req._load_session()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)

    def test_laod_session_session_id_no_user_id(self):
        # Cookie session_id but no user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)
        req = EngineAuthRequest.blank('/auth/google')
        req.cookies['_eauth'] = s.serialize()
        req._load_session()
        self.assertTrue(req.session.session_id == s.session_id)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)

    def test_laod_session_session_id_and_user_id(self):
        # Cookie session_id and user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)
        req = EngineAuthRequest.blank('/auth/google')
        req.cookies['_eauth'] = s.serialize()
        req._load_session()
        self.assertTrue(req.session.session_id == s.session_id)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)


    def test_laod_session_cookie_and_no_session(self):
        # Cookie and not session
        s = models.Session.create()
        old_sid = s.session_id
        s_serialized = s.serialize()
        s.key.delete()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 0)
        req = EngineAuthRequest.blank('/auth/google')
        req.cookies['_eauth'] = s_serialized
        req._load_session()
        # Assert that a new session was created
        self.assertTrue(req.session.session_id != old_sid)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)

    def test_save_session(self):
        # Cookie session_id but no user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)

        req = EngineAuthRequest.blank('/auth/google')
        req.cookies['_eauth'] = s.serialize()
        resp = req.get_response(app)
        resp.request = req
        resp._save_session()

        self.assertTrue(resp.request.session.session_id == s.session_id)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)

        # Add a user_id to session
        resp.request.session.user_id = '1'
        resp._save_session()
        # a new session should be created with the user_id as it's id
#        self.assertEqual(resp.request.session.key.id(), '1')
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)
        s1 = models.Session.query().get()
        self.assertEqual(s1.key.id(), '1')

