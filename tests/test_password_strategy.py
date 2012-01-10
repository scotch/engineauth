from webob import Request
import webob
from engineauth.middleware import AuthMiddleware
from engineauth import models
import test_base
import webapp2

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'

app = AuthMiddleware(webapp2.WSGIApplication())

class TestPasswordStrategy(test_base.BaseTestCase):

    def setUp(self):
        super(TestPasswordStrategy, self).setUp()

    def test_handle_request(self):
        email = 'test@example.com'
        pasword = 'password1'
        auth_id = 'password:{0}'.format(email)
        # No User or Profile
        user = models.User.get_by_auth_id(auth_id)
        self.assertEqual(user, None)
        p_count0 = models.UserProfile.query().count()
        u_count0 = models.User.query().count()
        self.assertEqual(p_count0, 0)
        self.assertEqual(u_count0, 0)
        # Create New User
        req = Request.blank('/auth/password',
            POST={'password': pasword, 'email': email})
        resp = req.get_response(app)
#        resp = req.call_application(app)
        # Retrieve user from datastore
        user = models.User.get_by_auth_id(auth_id)
        self.assertIn(auth_id, user.auth_ids)
        # Retrieve profile from datastore
        profile = models.UserProfile.get_by_id(auth_id)
        self.assertTrue(profile is not None)
        p_count1 = models.UserProfile.query().count()
        u_count1 = models.User.query().count()
        self.assertEqual(p_count1, 1)
        self.assertEqual(u_count1, 1)
        # Login User
        req = Request.blank('/auth/password',
            POST={'password': pasword, 'email': email})
        resp = req.get_response(app)
        # Make sure a new User is not created.
        p_count2 = models.UserProfile.query().count()
        u_count2 = models.User.query().count()
        self.assertEqual(p_count2, 1)
        self.assertEqual(u_count2, 1)
        # Wrong password
        req = Request.blank('/auth/password',
            POST={'password': 'fakepass', 'email': email})
        resp = req.get_response(app)

