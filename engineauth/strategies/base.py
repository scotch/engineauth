import threading
from webob import Request
import webob


def _abstract():
    raise NotImplementedError('You need to override this function')


class BaseStrategy(object):

    def __init__(self, app, config=None):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        req.provider_config = req.config['provider.{0}'.format(req.provider)]
        self.set_redirect(req)
        try:
            redirect_uri = self.handle_request(req)
        except Exception, e:
            redirect_uri = req.config['login_uri']
        resp = webob.exc.HTTPTemporaryRedirect(location=redirect_uri)
        resp.request = req
        return resp(environ, start_response)

    @property
    def options(self):
        return None

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

    def get_or_create_user_profile(self, auth_id, user_info,
                                   email=None, **kwargs):
        _abstract()

    def handle_request(self, req):
        _abstract()

    def add_user_to_session(self, req, user_id):
        req.session.user_id = user_id
        return req

    def set_redirect(self, req):
        next_uri = req.GET.get('next')
        if next_uri is not None:
            req.session.data['_redirect_uri'] = next_uri

    def get_redirect_uri(self, req):
        try:
            return str(req.session.data.pop('_redirect_uri'))
        except KeyError:
            return req.config['default_redirect_uri']