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

    def test__load_user(self):
        user = models.User.create_user('test:12345')
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()
        req.session.user_id = user.get_id()
        req._load_user()
        self.assertEqual(user, req.user)

    def test__load_user_by_profile(self):
        # No existing User no logged in User
        auth_id = 'test:12345'
        user_info = {
            'auth_id': auth_id,
            'info': {},
        }
        # create profile
        p = models.UserProfile.get_or_create(auth_id, user_info)
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()
        req._load_user()

        # User Count before
        user_count = models.User.query().count()
        self.assertEqual(user_count, 0)

        req.load_user_by_profile(p)

        # User Count after
        user_count = models.User.query().count()
        self.assertEqual(user_count, 1)

        user = models.User.query().get()
        self.assertTrue(p.key.id() in user.auth_ids)

        # Yes existing User no logged in User
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()
        req._load_user()

        req.load_user_by_profile(p)

        # Test to no new User was created
        user_count = models.User.query().count()
        self.assertEqual(user_count, 1)

        # Yes existing User yes logged in User new Profile
        auth_id = 'test:abc'
        user_info = {
            'auth_id': auth_id,
            'info': {},
            }
        # create profile
        p1 = models.UserProfile.get_or_create(auth_id, user_info)
        req.load_user_by_profile(p1)

        # Test to no new User was created
        user_count = models.User.query().count()
        self.assertEqual(user_count, 1)

    def test_add_message(self):
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()

        msgs = req.get_messages()
        self.assertEquals(msgs, None)

        req.add_message('TEST MESSAGE')
        msgs = req.get_messages()
        self.assertEquals(msgs, [{'level': None, 'message':'TEST MESSAGE' }])

        # Get again should be none.
        msgs = req.get_messages()
        self.assertEquals(msgs, None)

        # add message with level error
        req.add_message('TEST1', 'error')
        # add another message with level error
        req.add_message('TEST2', 'success')

        msgs = req.get_messages()
        self.assertEquals(msgs, [
                {'level': 'error', 'message':'TEST1' },
                {'level': 'success', 'message':'TEST2' },
        ])
        # Get again should be none.
        msgs = req.get_messages()
        self.assertEquals(msgs, None)

        # Test with different key.
        # add message with level error
        req.add_message('TEST1', 'error')
        # add another message with level error
        req.add_message('TEST2', 'success', '_mykey')

        msgs = req.get_messages()
        self.assertEquals(msgs, [
                {'level': 'error', 'message':'TEST1' },
        ])
        msgs_key = req.get_messages('_mykey')
        self.assertEquals(msgs_key, [
                {'level': 'success', 'message':'TEST2' },
        ])
        # Get again should be none.
        msgs = req.get_messages()
        self.assertEquals(msgs, None)
        msgs_key = req.get_messages()
        self.assertEquals(msgs_key, None)

    def test_set_redirect_uri(self):
        # test without next uri
        req = EngineAuthRequest.blank('/auth/google')
        req._load_session()
        req.set_redirect_uri()
        req._config = {'success_uri': '/callback'}
        redirect_uri = req.get_redirect_uri()
        self.assertEqual(redirect_uri, '/callback')

        # test with out next uri
        req = EngineAuthRequest.blank('/auth/google?next=/newcallback')
        req._load_session()
        req.set_redirect_uri()
        req._config = {'success_uri': '/callback'}
        redirect_uri = req.get_redirect_uri()
        self.assertEqual(redirect_uri, '/newcallback')

        req = EngineAuthRequest.blank('/auth/google?next=/newcallback&a=121&123=a')
        req._load_session()
        req.set_redirect_uri()
        req._config = {'success_uri': '/callback'}
        redirect_uri = req.get_redirect_uri()
        self.assertEqual(redirect_uri, '/newcallback')