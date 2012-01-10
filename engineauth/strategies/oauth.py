from __future__ import absolute_import
from apiclient.oauth import FlowThreeLegged
from engineauth.strategies.base import BaseStrategy
import httplib2
import cPickle as pickle

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'



def _abstract():
    raise NotImplementedError('You need to override this function')

class OAuthStrategy(BaseStrategy):

    def http(self, req):
        """Returns an authorized http instance.
        """
        if req.credentials is not None and not req.credentials.invalid:
            return req.credentials.authorize(httplib2.Http())

    def service(self, **kwargs):
        return _abstract()

    def start(self, req):
        authorize_url = req.flow.step1_get_authorize_url(
            oauth_callback=self.callback_uri)
        req.session.data[self.session_key] = pickle.dumps(req.flow)
        return authorize_url

    def callback(self, req):
        flow = pickle.loads(req.session.data.get(self.session_key))
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

        discovery = {
            'request': {
                'url': self.options['request_token_uri'],
                'parameters': {
                },
            },
            'authorize': {
                'url': self.options['authorize_uri'],
                'parameters': {
                    'oauth_token': {
                        'required': True,
                    },
                },
            },
            'access': {
                'url': self.options['access_token_uri'],
                'parameters': {
                },
            },
        }
        req.flow = FlowThreeLegged(
            discovery=discovery,
            consumer_key=req.provider_config.get('client_id'),
            consumer_secret=req.provider_config.get('client_secret'),
            user_agent='EngineAuth'
        )
        if not req.provider_params:
            return self.start(req)
        else:
            return self.callback(req)
