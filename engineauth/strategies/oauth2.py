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
import cPickle as pickle
from engineauth.strategies.base import BaseStrategy
import httplib2
from oauth2client.client import OAuth2WebServerFlow


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


def _abstract():
    raise NotImplementedError('You need to override this function')

class OAuth2Strategy(BaseStrategy):

    def http(self, req):
        """Returns an authorized http instance.
        """
        if req.credentials is not None and not req.credentials.invalid:
            return req.credentials.authorize(httplib2.Http())

    def service(self, **kwargs):
        return _abstract()

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
            self.raise_error('And Error has occurred. Please try again.')
        req.credentials = flow.step2_exchange(req.params)
        user_info = self.user_info(req)
        profile = self.get_or_create_profile(
            auth_id=user_info['auth_id'],
            user_info=user_info,
            credentials=req.credentials)
        req.load_user_by_profile(profile)
        return req.get_redirect_uri()

    def handle_request(self, req):
        self.callback_uri = '{0}{1}/{2}/callback'.format(req.host_url,
            self.config['base_uri'], req.provider)
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
