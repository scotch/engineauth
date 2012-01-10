from __future__ import absolute_import

from engineauth import models
from engineauth.strategies.base import BaseStrategy
from google.appengine.api import users

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'



def _abstract():
    raise NotImplementedError('You need to override this function')


class AppEngineOpenIDStrategy(BaseStrategy):

    def user_info(self, req):
        user = users.get_current_user()
        if user.federated_identity():
            auth_id = models.User.generate_auth_id(req.provider, user.federated_identity())
        else:
            auth_id = models.User.generate_auth_id(req.provider, user.user_id(), 'appengine')
        return {
            'auth_id': auth_id,
            'info': {
                'email': {
                    'value': user.email(),
                    },
                'nickname': user.nickname(),
                },
            }

    def start(self, req):
        provider_uri = req.GET['provider']
        return users.create_login_url(dest_url=self.callback_uri,
            federated_identity=provider_uri)

    def callback(self, req):
        user_info = self.user_info(req)
        profile = self.get_or_create_profile(
            auth_id=user_info['auth_id'],
            user_info=user_info)
        req.load_user_by_profile(profile)
        return req.get_redirect_uri()


    def handle_request(self, req):
        self.callback_uri = '{0}{1}/{2}/callback'.format(req.host_url,
            self.config['base_uri'], req.provider)
        if not req.provider_params:
            return self.start(req)
        else:
            return self.callback(req)
