from engineauth.middleware import AuthMiddleware
from engineauth import models
import test_base
import webapp2

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'

config = {
    'secret_key': 'CHANGE_TO_A_SECRET_KEY',
    'session_backend': 'datastore',
    'user_model': 'engineauth.models.User',
    'provider.google': {
        'client_id': '147940343938.apps.googleusercontent.com',
        'client_secret': '1QpwLBPRijdgfp4wdMx-TyDm',
        'api_key': 'AIzaSyBi5YLaEFHo9cUYhpldi5nxEk-xMWc3hiY',
        'scope': 'https://www.googleapis.com/auth/plus.me',
        },
    'provider.facebook': {
        'client_id': '',
        'client_secret': '',
        'scope': 'email',
        }
}

app = AuthMiddleware(webapp2.WSGIApplication(), config)

class TestAuthMiddleware(test_base.BaseTestCase):
    def setUp(self):
        super(TestAuthMiddleware, self).setUp()

    #    def test_load_config(self):
    #        req = webapp2.Request.blank('/auth/google')
    #        resp = req.get_response(app)
    #        self.assertEqual(resp, '/auth')

    def test_load_strategy(self):
        from engineauth.strategies.google import GoogleStrategy

        strategy_class = app.load_strategy('google')
        self.assertEqual(strategy_class, GoogleStrategy)
        self.assertRaises(Exception, app.load_strategy, 'enron')
        from engineauth.strategies.appengine_openid import\
            AppEngineOpenIDStrategy
        strategy_class = app.load_strategy('appengine_openid')
        self.assertEqual(strategy_class, AppEngineOpenIDStrategy)

    def test_load_session_no_session(self):
        req = webapp2.Request.blank('/auth/google')
        # No Session
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 0)
        sess = app.load_session(req)
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)

    def test_laod_session_session_id_no_user_id(self):
        # Cookie session_id but no user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)
        req = webapp2.Request.blank('/auth/google')
        req.cookies['_eauth'] = s.serialize()
        sess = app.load_session(req)
        self.assertTrue(sess.session_id == s.session_id)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)

    def test_laod_session_session_id_and_user_id(self):
        # Cookie session_id and user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)
        req = webapp2.Request.blank('/auth/google')
        req.cookies['_eauth'] = s.serialize()
        sess = app.load_session(req)
        self.assertTrue(sess.session_id == s.session_id)
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
        req = webapp2.Request.blank('/auth/google')
        req.cookies['_eauth'] = s_serialized
        sess = app.load_session(req)
        # Assert that a new session was created
        self.assertTrue(sess.session_id != old_sid)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)

    def test_save_session(self):
        # Cookie session_id but no user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)

        req = webapp2.Request.blank('/auth/google')
        req.cookies['_eauth'] = s.serialize()
        resp = req.get_response(app)
        resp.request = req
        sess = app.save_session(resp)

        self.assertTrue(sess.session_id == s.session_id)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertTrue(s_count2 == 1)

        # Add a user_id to session
        resp.request.session.user_id = '1'
        sess = app.save_session(resp)
        # a new session should be created with the user_id as it's id
        self.assertEqual(sess.key.id(), '1')
        s_count = models.Session.query().count()
        self.assertTrue(s_count == 1)
        s1 = models.Session.query().get()
        self.assertEqual(s1.key.id(), '1')

    def test_load_user(self):
        pass

    def test_save_user(self):
        pass
