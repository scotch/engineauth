from __future__ import absolute_import
import json
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy


class FacebookStrategy(OAuth2Strategy):
    def options(self):
        return {
            'provider': 'facebook',
            'site_uri': 'https://graph.facebook.com',
            'auth_uri': 'https://graph.facebook.com/oauth/authorize',
            'token_uri': 'https://graph.facebook.com/oauth/access_token',
            'default_redirect_uri': '/',
            }

    def user_info(self, req):
        url = "https://graph.facebook.com/me?access_token=" + \
              req.credentials.access_token
        res, results = self.http(req).request(url)
        if res.status is not 200:
            raise('A Facebook error.')
        user = json.loads(results)
        auth_id = User.generate_auth_id('facebook', user['id'])
        return {
            'auth_id': auth_id,
            'uid': user['id'],
            'info': {
                'id': user['id'],
                'displayName': user.get('name'),
                'name': {
                    'formatted': user.get('name'),
                    'familyName': user.get('last_name'),
                    'givenName': user.get('first_name'),
                    'middleName': user.get('middle_name'),
                    'honorificPrefix': None,
                    'honorificSuffix': None,
                },
                'birthday': user.get('birthday'), # user_birthday
                'gender': user.get('gender'),
                'utcOffset': user.get('timezone'),
                'locale': user.get('locale'),
                'verified': user.get('verified'),
                'email': user.get('email'), # email
                'nickname': user.get('username'), 
                'location': user.get('location'), # user_location
                'aboutMe': user.get('bio'),
                'image': {
                    'url': "http://graph.facebook.com/{0}/picture?type=square".format(user.get('id'))
                },
                'urls': [
                    {
                        'type': 'profile',
                        'value': user.get('link'),
                    }
                ],
            },
            'extra': {
                    'raw_info': user,
                }
        }


