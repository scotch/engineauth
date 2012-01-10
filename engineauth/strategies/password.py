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
        user_info['emails'] = [{'value': email, 'type': 'home', 'primary': True}]
        auth_id = models.User.generate_auth_id(req.provider, email)
        return {
            'auth_id': auth_id,
            'info': user_info,
            'extra': {
                'raw_info': user_info,
                }
        }

    def get_or_create_profile(self, auth_id, user_info, **kwargs):
        """
        Overrides to provide logic for checking and encrypting  passwords.
        :param auth_id:
        :param user_info:
        :param kwargs:
        :return:
        :raise:
        """
        password = kwargs.pop('password')
        profile = models.UserProfile.get_by_id(auth_id)
        if profile is None:
            # Create profile
            profile = models.UserProfile.get_or_create(auth_id, user_info,
                password=security.generate_password_hash(password, length=12))
        # Check password
        if not security.check_password_hash(password, profile.password):
            return self.raise_error('The password that you\'ve provided '
                                    'doesn\'t match our records. '
                                    'Please try again.')
        return profile

    def handle_request(self, req):
        # confirm that required fields are provided.
        password = req.POST['password']
        email = req.POST['email']
        if not password or not email:
            return self.raise_error('Please provide a valid email '
                                    'and a password.')
        user_info = self.user_info(req)
        profile = self.get_or_create_profile(
            auth_id=user_info['auth_id'],
            user_info=user_info,
            password=password)
        req.load_user_by_profile(profile)
        return req.get_redirect_uri()
