import json
import logging
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy


class SinaWeiboStrategy(OAuth2Strategy):

    @property
    def options(self):
        return {
            'provider': 'sinaweibo',
            'token_uri': 'https://api.weibo.com/oauth2/access_token',
            'auth_uri': 'https://api.weibo.com/oauth2/authorize',
        }

    def user_info(self, req):
        # get user id
        url = 'https://api.weibo.com/2/account/get_uid.json?access_token={}'.format(req.credentials.access_token)
        res, results = self.http(req).request(url)
        if res.status != 200:
            return self.raise_error('There was an error contacting Sina Weibo. Please try again.')
        uid = json.loads(results)['uid']
        # get user data
        url = 'https://api.weibo.com/2/users/show.json?uid={}&access_token={}'.format(uid, req.credentials.access_token)
        res, results = self.http(req).request(url)
        if res.status != 200:
            return self.raise_error('There was an error contacting Sina Weibo. Please try again.')
        user = json.loads(results)
        user_dict = {
            'auth_id': User.generate_auth_id(req.provider, user['id']),
            'uid': user['id'],
            'info': {
                'id': user.get('id'),
                'displayName': user.get('screen_name'),
                'name': {
                    'formatted': user.get('name')
                },
                'gender': user.get('gender'),
                'urls': [{
                    'value': user.get('url')
                }],
                'verified': user.get('verified'),
                'location': user.get('location'),
                'image': {
                    'url': user.get('profile_image_url')
                }
            },
            'extra': {
                'raw_info': user,
            }
        }
        return user_dict
