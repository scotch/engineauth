from engineauth import utils
try:
    from appengine_config import engineauth as user_config
except ImportError:
    user_config = None

default_config = {
    'base_uri': '/auth',
    'login_uri': '/login',
    'success_uri': '/',
    'redirect_back': False,
    'secret_key': 'CHANGE_TO_A_SECRET_KEY', # We add this here for testing only
    'user_model': 'engineauth.models.User',
    'provider.appengine_openid': {
        'class_path': 'engineauth.strategies.appengine_openid.AppEngineOpenIDStrategy',
        'required': ['email'],
        'uid': 'email',
        },
    'provider.facebook': {
        'class_path': 'engineauth.strategies.facebook.FacebookStrategy',
        'client_id': None,
        'client_secret': None,
        'scope': 'email',
        },
    'provider.github': {
        'class_path': 'engineauth.strategies.github.GithubStrategy',
        'client_id': None,
        'client_secret': None,
        },
    'provider.google': {
        'class_path': 'engineauth.strategies.google.GoogleStrategy',
        'client_id': None,
        'client_secret': None,
        'api_key': None,
        'scope': 'https://www.googleapis.com/auth/plus.me',
        },
    'provider.linkedin': {
        'class_path': 'engineauth.strategies.linkedin.LinkedInStrategy',
        'client_id': None,
        'client_secret': None,
        },
    'provider.password': {
        'class_path': 'engineauth.strategies.password.PasswordStrategy',
        'required': ['email'],
        'uid': 'email',
        },
    'provider.twitter': {
        'class_path': 'engineauth.strategies.twitter.TwitterStrategy',
        'client_id': None,
        'client_secret': None,
        },
    'provider.instagram': {
        'class_path': 'engineauth.strategies.instagram.InstagramStrategy',
        'client_id': None,
        'client_secret': None,
        },
    }

def load_config(cust_config=None):
    """

    :param cust_config:
    :return:
    """
    global user_config
    if cust_config is not None:
        user_config = cust_config
    return utils.load_config(default_config, user_config)
