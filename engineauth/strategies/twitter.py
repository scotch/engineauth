from __future__ import absolute_import
import json

from engineauth.models import User
from engineauth.strategies.oauth import OAuthStrategy


class TwitterStrategy(OAuthStrategy):

    @property
    def options(self):
        return {
            'provider': 'twitter',
            'request_token_uri': 'https://api.twitter.com/oauth/request_token',
            'access_token_uri': 'https://api.twitter.com/oauth/access_token',
            'authorize_uri': 'https://api.twitter.com/oauth/authenticate',
            }

    def service(self, **kwargs):
        pass

    def user_info(self, req):
        url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        res, results = self.http(req).request(url)
        if res.status != 200:
            raise('A {0} error.'.format(req.provider))
        user = json.loads(results)
        try:
            auth_id = User.generate_auth_id(req.provider, user['id'])
        except:
            raise('A {0} error.'.format(req.provider))

        return {
            'auth_id': auth_id,
            'info': {
                'id': user.get('id'), # Unique ID to the service provider
                'displayName': user.get('name'),
                'name': {
                    'formatted': user.get('name'),
#                    'familyName': user.get('family_name'),
#                    'givenName': user.get('given_name'),
#                    'middleName': user.get('middle_name'),
#                    'honorificPrefix': None,
#                    'honorificSuffix': None,
                },
                'urls': [
                        {
                        'type': 'twitter#profile',
                        'value': user.get('url'),
                        'primary': True,
                        },
                ],

                'utcOffset': user.get('utc_offset'),
                'locale': user.get('lang'),
                'verified': user.get('verified'),
                'nickname': user.get('screen_name'),
                'location': user.get('location'), # user_location
                'aboutMe': user.get('description'),
                'photos':  [
                    {
                        'value': user.get('profile_image_url'),
                        'type': 'full'
                    },
                    {
                        'value': user.get('profile_image_url_https'),
                        'type': 'https'
                    },
                ],
                'image': {
                        'url': user.get('profile_image_url'),
                    },
            },
            'extra': {
                'raw_info': user,
                },
        }
