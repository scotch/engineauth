"""
    engineauth.strategies.oauth2
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
import httplib2
from oauth2client.client import OAuth2WebServerFlow
import cPickle as pickle


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


def _abstract():
    raise NotImplementedError('You need to override this function')


class Error(Exception):

    def handle_error(self, error):
        self.add_message('The authorization request failed: {0}'.format(error), level='error')
        return self.redirect(self.login_uri())


class OAuth2Strategy(BaseStrategy):

    def http(self, req):
        """Returns an authorized http instance.
        """
        if req.credentials is not None and not req.credentials.invalid:
            return req.credentials.authorize(httplib2.Http())

    def service(self, **kwargs):
        return _abstract()

    def get_or_create_user_profile(self, auth_id, user_info,
                                   email=None, **kwargs):
        user = models.User.get_or_create(auth_id, email)
        profile = models.Profile.get_or_create(auth_id, user_info,
            credentials=kwargs.get('credentials'))
        return user, profile

    def start(self, req):
        # Store the request URI in 'state' so we can use it later
        req.flow.params['state'] = req.path_url
        authorize_url = req.flow.step1_get_authorize_url(self.callback_uri)
        req.session.data[self.session_key] = pickle.dumps(req.flow)
        return authorize_url

    def callback(self, req):
        if req.GET.get('error'): return req.GET.get('error')
        flow = pickle.loads(str(req.session.data.get(self.session_key)))
        if flow is None:
            raise Exception('Pickle error')
        req.credentials = flow.step2_exchange(req.params)
        user_info = self.user_info(req)
        user, profile = self.get_or_create_user_profile(
            auth_id=user_info['auth_id'],
            user_info=user_info,
            email=user_info.get('info').get('email'),
            credentials=req.credentials)
        self.add_user_to_session(req, user.get_id())
        return self.get_redirect_uri(req)


    def handle_request(self, req):
        self.callback_uri = '{0}{1}/{2}/callback'.format(req.host_url,
            req.config['base_uri'], req.provider)
        self.session_key = '_auth_strategy:{0}'.format(req.provider)
        req.flow = OAuth2WebServerFlow(
            req.provider_config.get('client_id'),
            req.provider_config.get('client_secret'),
            req.provider_config.get('scope', ''),
            auth_uri=self.options['auth_uri'],
            token_uri=self.options['token_uri'],
        )
        if not req.provider_params:
            return self.start(req)
        else:
            return self.callback(req)
