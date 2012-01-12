import threading
from webob import Request
import webob
from engineauth import models
from engineauth.middleware import EngineAuthRequest


class Error(Exception):
    """Base user exception."""

class EngineAuthError(Error):
    def __init__(self, msg):
        self.message = msg

def _abstract():
    raise NotImplementedError('You need to override this function')


class BaseStrategy(object):

    error_class = EngineAuthError

    def __init__(self, app, config=None):
        self.app = app
        self.config = config

    def __call__(self, environ, start_response):
        req = EngineAuthRequest(environ)
        req._config = self.config
        req.provider_config = self.config['provider.{0}'.format(req.provider)]
        # TODO: This area needs to be reworked. There needs to be
        # a better way to handle errors
        try:
            redirect_uri = self.handle_request(req)
        except Exception, e:
            req.add_message(e.message, level='error')
            redirect_uri = self.config['login_uri']
        resp = webob.exc.HTTPTemporaryRedirect(location=redirect_uri)

        resp.request = req
        return resp(environ, start_response)

    @property
    def options(self):
        """
        Strategy Options must be overridden by sub-class
        :return:
        """
        return _abstract()

    def user_info(self, req):
        """

        :param req:
        :returns dict() Portable Contacts spec
        {
            'auth_id': User.generate_auth_id(req.provider, user['id']),
            'uid': user['id'], # Unique ID to the service provider
            'info': {
                'id': user.get('id'),
                'displayName': user.get('name'),
                'name': {
                    'formatted': user.get('name'),
                    'familyName': user.get('family_name'),
                    'givenName': user.get('given_name'),
                    'middleName': user.get('middle_name'),
                    'honorificPrefix': None,
                    'honorificSuffix': None,
                    },
                'birthday': user.get('birthday'),
                'gender': user.get('gender'),
                'tags': user.get('tags'), # List of tags
                'emails': [
                    {
                        'value': user.get('email'), # email
                        'type': user.get('email').get('type'), # home, work
                        'primary': user.get('email').get('primary'), # boolean
                    },
                ],
                'urls': [
                    {
                        'type': 'work',
                        'value': user.get('url'),
                        'primary': user.get('url').get('primary'),
                    },
                ],
                'phoneNumbers': [
                    {
                        'type': 'work',
                        'value': user.get('phone_number'),
                        'primary': True,
                    },
                ],
                "photos": [
                    {
                        "value": "http://sample.site.org/photos/12345.jpg",
                        "type": "thumbnail"
                    }
                ],
                "ims": [
                    {
                        "value": "plaxodev8",
                        "type": "aim"
                    }
                ],
                "addresses": [
                    {
                        "type": "home",
                        "streetAddress": "742 Evergreen Terrace\nSuite 123",
                        "locality": "Springfield",
                        "region": "VT",
                        "postalCode": "12345",
                        "country": "USA",
                        "formatted": "742 Evergreen Terrace\nSuite 123\nSpringfield, VT 12345 USA"
                    }
                ],
                "organizations": [
                    {
                        "name": "Burns Worldwide",
                        "title": "Head Bee Guy"
                    }
                ],
                "accounts": [
                    {
                        "domain": self.provider,
                        "userid": user['id']
                    }
                ],
                'utcOffset': user.get('utc_offset'),
                'locale': user.get('locale'),
                'verified': user.get('verified'),
                'nickname': user.get('username'),
                'location': user.get('location'), # user_location
                'aboutMe': user.get('bio'),
                'image': {
                    'url': user.get('id')),
                },

            },
            'extra': {
                'raw_info': user,
                }
        }
        """
        _abstract()

    def get_or_create_profile(self, auth_id, user_info, **kwargs):
        return models.UserProfile.get_or_create(auth_id, user_info, **kwargs)

    def handle_request(self, req):
        _abstract()

    def raise_error(self, message):
        raise EngineAuthError(msg=message)
