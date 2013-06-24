from __future__ import absolute_import
import json
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy


class GithubStrategy(OAuth2Strategy):

    @property
    def options(self):
        return {
            'provider': 'github',
            'site_uri': 'https://api.github.com',
            'auth_uri': 'https://github.com/login/oauth/authorize',
            'token_uri': 'https://github.com/login/oauth/access_token',
            }

    def user_info(self, req):
        url = "https://api.github.com/user?access_token=" +\
              req.credentials.access_token
        res, results = self.http(req).request(url)
        if res.status is not 200:
            return self.raise_error('There was an error contacting Github. '
                                    'Please try again.')
        user = json.loads(results)
        auth_id = User.generate_auth_id(req.provider, user['id'])
        return {
            'auth_id': auth_id,
            'info': {
                'id': user['id'],
                'displayName': user.get('name'),
                'name': {
                    'formatted': user.get('name'),
#                    'familyName': user.get('last_name'),
#                    'givenName': user.get('first_name'),
#                    'middleName': user.get('middle_name'),
#                    'honorificPrefix': None,
#                    'honorificSuffix': None,
                    },
#                'birthday': user.get('birthday'), # user_birthday
#                'gender': user.get('gender'),
#                'utcOffset': user.get('timezone'),
#                'locale': user.get('locale'),
#                'verified': user.get('verified'),
                'emails': [
                    {
                        'value': user.get('email'), # email
                        'type': None, # home, work
                        'primary': True # boolean
                    },
                ],
                'nickname': user.get('username'),
                'location': user.get('location'),
                'aboutMe': user.get('bio'),
                'company': user.get('company'),
                'image': {
                    'url': user.get('avatar_url'),
                },
                'urls': [
                    {
                        'type': 'github',
                        'value': user.get('html_url'),
                    },
                    {
                        'type': 'blog',
                        'value': user.get('blog'),
                    },
                ],
                },
            'extra': {
                'raw_info': user,
                }
        }


