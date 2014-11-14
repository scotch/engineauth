from __future__ import absolute_import
from engineauth import models
from engineauth import utils
from engineauth.config import load_config
import re
import traceback
from webob import Response
from webob import Request

class EngineAuthResponse(Response):

    def _save_session(self):
        session = self.request.session
        # Compare the hash that we set in load_session to the current one.
        # We only save the session and cookie if this value has changed.
        if self.request.session_hash == session.hash():
            return session
        session.put()
        # If we have a user_id we want to updated the
        # session to use the user_id as the key.
        if session.user_id is not None:
            session_id = session.key.id()
            if session_id != session.user_id:
                session = models.Session.upgrade_to_user_session(
                    session_id, session.user_id)
        self.set_cookie('_eauth', session.serialize())
        return self

    def _save_user(self):
        pass


class EngineAuthRequest(Request):

    ResponseClass = EngineAuthResponse

    def _load_session(self):
        value = self.cookies.get('_eauth')
        session = None
        if value:
            session = models.Session.get_by_value(value)
        if session is not None:
            # Create a hash for later comparison,
            # to determine if a put() is required
            session_hash = session.hash()
        else:
            session = models.Session.create()
            # set this to False to ensure a cookie
            # is saved later in the response.
            session_hash = '0'
        self.session = session
        self.session_hash = session_hash
        return self

    def _get_user_class(self):
        try:
            return utils.import_class(self._config['user_model'])
        except Exception:
            return models.User

    def _load_user(self):
        if self.session is not None and self.session.user_id:
            self.user = self._get_user_class().get_by_id(int(self.session.user_id))
            if self.user is None:
                # TODO: If the user_id from the session returns no user,
                # then remove it.
                pass
        else:
            self.user = None
        return self

    def _load_user_by_profile(self, profile):
        # if the user is logged in update that user with the profile details
        if self.user:
            self.user.add_profile(profile)
        # else get or create a user based on the profile
        else:
            self.user = self._get_user_class().get_or_create_by_profile(profile)
        # Add user to session
        self.session.user_id = self.user.get_id()
    load_user_by_profile = _load_user_by_profile

    def _add_message(self, message, level=None, key='_messages'):
        if not self.session.data.get(key):
            self.session.data[key] = []
        return self.session.data[key].append({
            'message': message, 'level': level})
    add_message = _add_message

    def _get_messages(self, key='_messages'):
        try:
            return self.session.data.pop(key)
        except KeyError:
            pass
    get_messages = _get_messages

    def _set_redirect_back(self):
         next_uri = self.referer
         if next_uri is not None and self._config['redirect_back']:
            self.session.data['_redirect_uri'] = next_uri
    set_redirect_uri = _set_redirect_back

    def _get_redirect_uri(self):
        try:
            return self.session.data.pop('_redirect_uri').encode('utf-8')
        except KeyError:
            return self._config['success_uri']
    get_redirect_uri = _get_redirect_uri

    def _set_globals(self, environ):
#        environ['ea.config'] = req.config
        environ['ea.session'] = self.session
        environ['ea.user'] = self.user


class AuthMiddleware(object):
    def __init__(self, app, config=None):
        self.app = app
        self._config = load_config(config)
        self._url_parse_re = re.compile(r'%s/([^\s/]+)/*(\S*)' %
                                        (self._config['base_uri']))

    def __call__(self, environ, start_response):
        # If the request is to the admin, return
        if environ['PATH_INFO'].startswith('/_ah/'):
            return self.app(environ, start_response)
        # load session
        req = EngineAuthRequest(environ)
        req._config = self._config
        req._load_session()
        req._load_user()
        if req._config['redirect_back']:
            req._set_redirect_back()
        resp = None
        # If the requesting url is for engineauth load the strategy
        if environ['PATH_INFO'].startswith(self._config['base_uri']):
            # extract provider and additional params from the url
            provider, provider_params = self._url_parse_re.match(
                req.path_info).group(1, 2)
            if provider:
                req.provider = provider
                req.provider_params = provider_params
                # load the desired strategy class
                strategy_class = self._load_strategy(provider)
                resp = req.get_response(strategy_class(self.app, self._config))
                if resp.request is None:
                    # TODO: determine why this is necessary.
                    resp.request = req
        if resp is None:
            resp = req.get_response(self.app)
        # Save session, return response
        resp._save_session()
        return resp(environ, start_response)

    def _load_strategy(self, provider):
        try:
            strategy_location = self._config[
                                'provider.{0}'.format(provider)]['class_path']
            return utils.import_class(strategy_location)
        except Exception, e:
            traceback.print_exc()
            raise(Exception, "You must provide a location for the {0} "\
                             "strategy. Add a 'location' key to the "\
                             "'provider.{0}' config dict".format(provider))

