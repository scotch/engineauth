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
            'uid': auth_id,
            'user_info': {
                'email': {
                    'value': user.email(),
                    },
                'nickname': user.nickname(),
                },
            }

    def get_or_create_user_profile(self, auth_id, user_info,
                                   email=None, **kwargs):
        user = models.User.get_or_create(auth_id, email)
        profile = models.Profile.get_or_create(auth_id, user_info)
        return user, profile

    def start(self, req):
        self.set_redirect(req)
        try:
            provider_uri = req.GET['provider']
            return users.create_login_url(dest_url=self.callback_uri,
                federated_identity=provider_uri)
        except Exception, e:
            raise e

    def callback(self, req):
        user_info = self.user_info(req)
        try:
            user, profile = self.get_or_create_user_profile(
                auth_id=user_info['uid'],
                email=user_info.get('email'),
                user_info=user_info)
            self.add_user_to_session(req, user.get_id())
            return self.get_redirect_uri(req)
        except Exception, e:
            # TODO: Handle error
            raise e

    def handle_request(self, req):
        self.callback_uri = '{0}{1}/{2}/callback'.format(req.host_url,
            req.config['base_uri'], req.provider)
        if not req.provider_params:
            return self.start(req)
        else:
            return self.callback(req)


