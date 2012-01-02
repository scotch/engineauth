"""
    engineauth.strategies.password
    ============================

    OAuth2 Authentication Strategy
    :copyright: (c) 2011 Kyle Finley.
    :license: Apache Sotware License, see LICENSE for details.

    :copyright: (c) 2010 Google Inc.
    :license: Apache Software License, see LICENSE for details.
"""
from __future__ import absolute_import
from engineauth import models
from engineauth.strategies.base import BaseStrategy
from webapp2_extras import security


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class PasswordStrategy(BaseStrategy):

    def user_info(self, req):
        email = req.POST['email']
        user_info = req.POST.get('user_info', {})
        user_info['email'] = {'value': email, 'type': 'home', 'primary': True}
        auth_id = models.User.generate_auth_id(req.provider, email)
        return {
            'uid': auth_id,
            'info': user_info,
            'extra': {
                'raw_info': user_info,
                }
        }

    def get_or_create_user_profile(self, auth_id, user_info,
                                   email=None, **kwargs):
        password = kwargs.pop('password')
        user = models.User.get_or_create(auth_id, email)
        profile = models.Profile.get_by_id(auth_id)
        if profile is None:
            # Create profile
            profile = models.Profile.get_or_create(auth_id, user_info,
                password=security.generate_password_hash(password, length=12))
        # Check password
        if not security.check_password_hash(password, profile.password):
            raise('Incorrect Password')
        return user, profile

    def handle_request(self, req):
        # confirm that required fields are provided.
        password = req.POST['password']
        user_info = self.user_info(req)

        user, profile = self.get_or_create_user_profile(
            auth_id=user_info['auth_id'],
            user_info=user_info,
            email=user_info.get('info').get('email'),
            password=password)
        self.add_user_to_session(req, user.get_id())
        return self.get_redirect_uri(req)
