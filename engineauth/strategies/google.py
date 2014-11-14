from __future__ import absolute_import

from apiclient.discovery import build
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy
from google.appengine.api import memcache
import httplib2
import traceback


class GoogleStrategy(OAuth2Strategy):

    @property
    def options(self):
        return {
            'provider': 'google',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
        }

    def service(self, **kwargs):
        name = kwargs.get('name', 'plus')
        version = kwargs.get('version', 'v1')
        return build(name, version, http=httplib2.Http(memcache))

    def user_info(self, req):
        try:
            user = self.service().people().get(userId='me').execute(self.http(req))
            auth_id = User.generate_auth_id('google', user['id'], 'plus')
            urls = user.get('urls') or []
            if user.get('url'):
                urls.append({u'type':u'google#plus', u'value': user.get('url')})
        except Exception:
            traceback.print_exc()
            return self.raise_error('There was an error contacting Google Plus. '
                                    'Note this strategy requires a Google Plus Account. '
                                    'If you have a Google Plus Account '
                                    'please try again.')
        return {
            'auth_id': auth_id,
            'info': {
                'id': user['id'],
                'displayName': user.get('displayName'),
            },
            'extra': {
                'raw_info': user,
                }
        }
