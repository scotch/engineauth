Dependencies
============
- `ndb <http://code.google.com/p/appengine-ndb-experiment/>`_ - EngineAuth uses features of ndb that are only available in master. This requirement will be removed by after the next sdk update.
- `oauth2client <http://code.google.com/p/google-api-python-client/>`_ - Required for OAuth2 Strategies
- `httplib2 <http://code.google.com/p/google-api-python-client/>`_ - Required for OAuth and OAuth2 Strategies
- `uri-templates <http://code.google.com/p/uri-templates>`_ - Required for OAuth and OAuth2 Strategies
- `python-gflags <http://code.google.com/p/python-gflags>`_ - Required for OAuth and OAuth2 Strategies
- `python-oauth2 <http://github.com/simplegeo/python-oauth2>`_ - Required for OAuth Strategies

Installation
============
Copy ``engineauth`` directory and the contents of ``lib`` directory to your project's ``root`` directory.

Configuring EngineAuth
**********************

In your ``appengine_config.py`` add::

    def webapp_add_wsgi_middleware(app):
        from engineauth import middleware
        return middleware.AuthMiddleware(app)

    engineauth = {
    #    'base_url': 'auth',
        'secret_key': 'CHANGE_TO_A_SECRET_KEY',
        'session_backend': 'datastore',
        'user_model': 'engineauth.models.User',
    }

    engineauth['provider.auth'] = {
        'user_model': 'engineauth.models.User',
        'session_backend': 'datastore',
    }

    # Facebook Authentication
    engineauth['provider.facebook'] = {
        'client_id': 'CHANGE_TO_FACEBOOK_APP_ID',
        'client_secret': 'CHANGE_TO_FACEBOOK_CLIENT_SECRET',
        'scope': 'email',
    }

    # Google Plus Authentication
    engineauth['provider.google'] = {
        'client_id': 'CHANGE_TO_GOOGLE_CLIENT_ID',
        'client_secret': 'CHANGE_TO_GOOGLE_CLIENT_SECRET',
        'api_key': 'CHANGE_TO_GOOGLE_API_KEY',
        'scope': 'https://www.googleapis.com/auth/plus.me',
    }

    # Twitter Authentication
    engineauth['provider.twitter'] = {
        'client_id': 'l8nfb1saEW4mlTOARqunKg',
        'client_secret': 'LCQweRuuGndhtNWihnwiDxs9npkNRII8GAgpGkYFi5c',
    }

Acquiring Client Keys
*********************

Facebook
--------
1. Go to: https://developers.facebook.com/apps
2. Select your application
3. Under ``Select how your app integrates with Facebook`` click ``Website``. In the ``Site URL:`` field enter your domain E.g. http://example.com/ or http://localhost:8080/ be sure to include the closing ``/``.
3. Copy ``App ID/API Key`` as ``client_id``
4. Copy ``App Secret`` as ``client_secret``

.. Note::
    Zuckerberg won't allow you to specify multiple callback domains for a single application. So for development you must create a separate application. Then, in your ``appengine_config.py`` you can then specify which config will be loaded at runtime.

E.g.::

    import os
    ON_DEV = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
    if ON_DEV:
        # Facebook settings for Development
        engineauth['provider.facebook'] = {
            'client_id': 'DEVELOPMENT_APP_KEY',
            'client_secret': 'DEVELOPMENT_APP_SECRET',
            'scope': 'email',
            }
    else:
        # Facebook settings for Production
        engineauth['provider.facebook'] = {
            'client_id': 'PRODUCTION_APP_KEY',
            'client_secret': 'PRODUCTION_APP_SECRET',
            'scope': 'email',
            }

Google Plus
-----------
1. Go to: https://code.google.com/apis/console
2. Select your application or create a new one.
3. Choose ``API Access``
4. If you have not generated a client id, do so.

Twitter
-------
1. Go to: https://dev.twitter.com/apps
2. Select your application or create a new one.
3. Make sure the you set the callback to YOUR_APPLICATION_URL/auth/twitter/callback. It's fine to set this to your production url, EngineAuth passes a redirect url while authenticating so there's no need to specify the localhost:8080 here.
4. Go to Details OAuth settings
5. Copy ``Consumer key`` as ``client_id``
6. Copy ``Consumer secret`` as ``client_secret``


App Engine OpenID
-----------------
1. Go to: https://appengine.google.com
2. Select your application
3. Choose ``Application Settings``
4. Choose ``(Experimental Federated Login)`` from the ``Authentication Options`` drop down
5. Click Save

