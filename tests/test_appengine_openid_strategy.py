from engineauth import models
from engineauth.middleware import AuthMiddleware
import test_base
import webapp2
from webob import Request

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'

app = AuthMiddleware(webapp2.WSGIApplication())



class TestAppEngineOpenIDStrategy(test_base.BaseTestCase):
    def setUp(self):
        super(TestAppEngineOpenIDStrategy, self).setUp()

    def test_handle_request(self):
        # No User or Profile
        p_count0 = models.UserProfile.query().count()
        u_count0 = models.User.query().count()
        self.assertEqual(p_count0, 0)
        self.assertEqual(u_count0, 0)
        # Create New User
        provider = 'gmail.com'
        req = Request.blank('/auth/appengine_openid?provider=' + provider)
        resp = req.get_response(app)
        self.assertEqual(resp.location, 'https://www.google.com/accounts/'
                                        'Login?continue=http%3A//localhost/'
                                        'auth/appengine_openid/callback')

#        # Retrieve user from datastore
#        user = models.User.get_by_auth_id(auth_id)
#        self.assertIn(auth_id, user.auth_ids)
#        self.assertTrue(user._has_email(email))
#        # Retrieve profile from datastore
#        profile = models.UserProfile.get_by_id(auth_id)
#        self.assertTrue(profile is not None)
#        p_count1 = models.UserProfile.query().count()
#        u_count1 = models.User.query().count()
#        self.assertEqual(p_count1, 1)
#        self.assertEqual(u_count1, 1)
#        # Login User
#        req = Request.blank('/auth/appengine_openid?provider=' + provider)
#        resp = req.get_response(app)
#        # Make sure a new User is not created.
#        p_count2 = models.UserProfile.query().count()
#        u_count2 = models.User.query().count()
#        self.assertEqual(p_count2, 1)
#        self.assertEqual(u_count2, 1)

