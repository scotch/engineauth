from __future__ import absolute_import
import json
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy

class InstagramStrategy(OAuth2Strategy):

    @property
    def options(self):
        
        return {
            'provider': 'instagram',
            'site_uri': 'https://api.instagram.com',
            'auth_uri': 'https://api.instagram.com/oauth/authorize',
            'token_uri': 'https://api.instagram.com/oauth/access_token',
        }
    
    def service(self, **kwargs):
        pass

    def user_info(self, req):
        url = "https://api.instagram.com/v1/users/self/?access_token=" + \
              req.credentials.access_token
        res, results = self.http(req).request(url)
        if res.status is not 200:
            return self.raise_error('There was an error contacting Instagram. '
                                    'Please try again.')
        user = json.loads(results)['data']
        auth_id = User.generate_auth_id(req.provider, user['id'])
        return {
            'auth_id': auth_id,
            'info': {
                'id': user['id'],
                'displayName': user.get('username'),
                'name': {
                    'formatted': user.get('full_name'),
#                    'familyName': user.get('last_name'),
#                    'givenName': user.get('first_name'),
#                    'middleName': user.get('middle_name'),
#                    'honorificPrefix': None,
#                    'honorificSuffix': None,
                },
                'nickname': user.get('username'),
                'aboutMe': user.get('bio'),
                'image': {
                    'url': user.get('profile_picture')
                },
                'urls': [
                    {
                        'type': 'website',
                        'value': user.get('website'),
                    },
                    
                ],
            },
            'extra': {
                    'raw_info': user,
                }
        }

