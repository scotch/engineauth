from __future__ import absolute_import

from apiclient.discovery import build
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy
from google.appengine.api import memcache
import httplib2


class GoogleStrategy(OAuth2Strategy):

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
        user = self.service().people().get(userId='me').execute(self.http(req))
        auth_id = User.generate_auth_id('google', user['id'], 'plus')
        return {
            'auth_id': auth_id,
            'uid': user['id'],
            'info': {
                'id': user['id'],
                'displayName': user.get('displayName'),
#                'name': {
#                    'formatted': user.get('name'),
#                    'familyName': user.get('last_name'),
#                    'givenName': user.get('first_name'),
#                    'middleName': user.get('middle_name'),
#                    'honorificPrefix': None,
#                    'honorificSuffix': None,
#                    },
#                'birthday': user.get('birthday'), # user_birthday
#                'gender': user.get('gender'),
#                'timezone': user.get('timezone'),
#                'locale': user.get('locale'),
#                'verified': user.get('verified'),
#                'email': user.get('email'), # email
#                'nickname': user.get('username'),
#                'location': user.get('location'), # user_location
#                'aboutMe': user.get('aboutMe'),
                'image': {
                    'url': user.get('image').get('url'),
                },
#                'urls': [
#                    {
#                        'type': 'profile',
#                        'value': user.get('link'),
#                    }
#                ],
            },
            'extra': {
                'raw_info': user,
                }
        }

