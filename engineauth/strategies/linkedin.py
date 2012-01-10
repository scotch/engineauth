from __future__ import absolute_import
import json

from engineauth.models import User
from engineauth.strategies.oauth import OAuthStrategy


class LinkedInStrategy(OAuthStrategy):

    @property
    def options(self):
        return {
            'provider': 'linkedin',
            'request_token_uri': 'https://api.linkedin.com/uas/oauth/requestToken',
            'access_token_uri': 'https://api.linkedin.com/uas/oauth/accessToken',
            'authorize_uri': 'https://www.linkedin.com/uas/oauth/authenticate',
            }

    def fields(self):
        return ["id", "first-name", "last-name", "headline", "industry",
                "picture-url", "public-profile-url"]

    def service(self, **kwargs):
        pass

    def user_info(self, req):
        url = "http://api.linkedin.com/v1/people/~:({0})?format=json".format(
            ','.join(self.fields()))
        res, results = self.http(req).request(url)
        if res.status is not 200:
            return self.raise_error('There was an error contacting LinkedIn. Please try again.')
        user = json.loads(results)
        auth_id = User.generate_auth_id(req.provider, user['id'])
        return {
            'auth_id': auth_id,
            'info': {
                'id': user.get('id'), # Unique ID to the service provider
                'displayName': "{0} {1}".format(user.get('firstName'), user.get('lastName')),
                'name': {
                    'formatted': "{0} {1}".format(user.get('firstName'), user.get('lastName')),
                    'familyName': user.get('lastName'),
                    'givenName': user.get('firstName'),
#                    'middleName': user.get('middle_name'),
                    'honorificPrefix': None,
                    'honorificSuffix': None,
                },
                'urls': [
                        {
                        'type': 'linkedin#profile',
                        'value': user.get('publicProfileUrl'),
                        'primary': True,
                        },
                ],
                'industry': user.get('industry'),
#                'utcOffset': user.get('utc_offset'),
#                'locale': user.get('lang'),
#                'verified': user.get('verified'),
#                'nickname': user.get('screen_name'),
#                'location': user.get('location'), # user_location
                'aboutMe': user.get('headline'),
#                'photos':  [
#                        {
#                        'value': user.get('profile_image_url'),
#                        'type': 'full'
#                    },
#                        {
#                        'value': user.get('profile_image_url_https'),
#                        'type': 'https'
#                    },
#                ],
                'image': {
                    'url': user.get('pictureUrl'),
                    },
                },
            'extra': {
                'raw_info': user,
                },
            }
