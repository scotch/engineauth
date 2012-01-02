from __future__ import absolute_import
import appengine_config
from engineauth import utils
from engineauth import models
import re
from webob import Request


default_config = {
    'base_uri': '/auth',
    'login_uri': '/login',
    'default_redirect_uri': '/',
    'provider.appengine_openid': {
        'class_path': 'engineauth.strategies.appengine_openid.AppEngineOpenIDStrategy',
        'required': ['email'],
        'uid': 'email',
        },
    'provider.facebook': {
        'class_path': 'engineauth.strategies.facebook.FacebookStrategy',
        'client_id': None,
        'client_secret': None,
        'scope': 'email',
        },
    'provider.google': {
        'class_path': 'engineauth.strategies.google.GoogleStrategy',
        'client_id': None,
        'client_secret': None,
        'api_key': None,
        'scope': 'https://www.googleapis.com/auth/plus.me',
        },
    'provider.password': {
        'class_path': 'engineauth.strategies.password.PasswordStrategy',
        'required': ['email'],
        'uid': 'email',
        },
    'provider.twitter': {
        'class_path': 'engineauth.strategies.twitter.TwitterStrategy',
        'client_id': None,
        'client_secret': None,
        },
    }


class AuthMiddleware(object):
    def __init__(self, app, config=None):
        self.app = app
        assert config or appengine_config.engineauth,\
        'You must pass provide config settings.'
        if config is None:
            config = appengine_config.engineauth
        self._config = utils.load_config(default_config, config)
        self._url_parse_re = re.compile(r'%s/([^\s/]+)/*(\S*)' %
                                        (self._config['base_uri']))

    def __call__(self, environ, start_response):
        # load session
        req = Request(environ)
        req.session = self.load_session(req)
        # Create a hash for later comparison, to determine if a put() is required
        req.session_hash = req.session.hash()
        req.user = self.load_user(req)
        # If the requesting url doesn't start with base_url return
        if not environ['PATH_INFO'].startswith(self._config['base_uri']):
            return self.app(environ, start_response)
            # extract provider and additional params from the url
        provider, provider_params = self._url_parse_re.match(
            req.path_info).group(1, 2)
        if provider is None:
            # TODO: maybe we load html here with links to strategies.
            return self.app(environ, start_response)
        req.provider = provider
        req.provider_params = provider_params
        req.config = self._config
        # load the desired strategy class
        strategy_class = self.load_strategy(provider)
        strategy_resp = req.get_response(strategy_class(self.app))
        if strategy_resp.request is None:
            # TODO: determine why this is necessary.
            strategy_resp.request = req
        self.save_session(strategy_resp)
        self.set_globals(environ, req)
        return strategy_resp(environ, start_response)

    def set_globals(self, environ, req):
        environ['ea.config'] = req.config
        environ['ea.session'] = req.session
        environ['ea.user'] = req.user

    def load_strategy(self, provider):
        try:
            strategy_location = self._config[
                                'provider.{0}'.format(provider)]['class_path']
            return utils.import_class(strategy_location)
        except Exception, e:
            raise(Exception, "You must provide a location for the {0} "\
                             "strategy. Add a 'location' key to the "\
                             "'provider.{0}' config dict".format(provider))

    def load_session(self, req):
        value = req.cookies.get('_eauth')
        s = None
        if value:
            s = models.Session.get_by_value(value)
        if s is None:
            s = models.Session.create()
        return s

    def save_session(self, resp):
        session = resp.request.session
        if resp.request.session_hash == session.hash():
            return session
        session.put()
        # If we have a user_id we want to updated the
        # session to use the user_id as the key.
        if session.user_id is not None:
            session_id = session.key.id()
            if session_id != session.user_id:
                session = models.Session.upgrade_to_user_session(
                    session_id, session.user_id)
        resp.set_cookie('_eauth', session.serialize())
        return session

    def load_user(self, req):
        if req.session is not None and req.session.user_id:
            return models.User.get_by_id(req.session.user_id)
        return None

    def save_user(self):
        pass