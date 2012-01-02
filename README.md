# EngineAuth: Google App Engine Multi-Authentication Simplified. #

## Dependancies ##

[oauth2client](http://code.google.com/p/google-api-python-client/)

[httplib2](http://code.google.com/p/httplib2)

[uri-templates](http://code.google.com/p/uri-templates)

[python-gflags](http://code.google.com/p/python-gflags)

[python-oauth2](http://github.com/simplegeo/python-oauth2)

## Installation ##

- Copy `engineauth` directory and the contents of `lib` directory to your project's `root` directory.

### Acquiring Client Keys ###

#### Facebook ####
1. Go to: [https://developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Select your application
3. Copy `App ID/API Key` as `client_id`
4. Copy `App Secret` as `client_secret`

#### Google Plus ####

1. Go to: [https://code.google.com/apis/console](https://code.google.com/apis/console)
2. Select your application
3. Choose `API Access`
4. If you have not generated a client id, do so.

#### AppEngine OpenID ####

1. Go to: [https://appengine.google.com](https://appengine.google.com)
2. Select your application
3. Choose `Application Settings`
4. Choose `(Experimental Federated Login)` from the `Authentication Options` drop down
5. Click Save

In your `app.yaml` add:

```yaml

- url: /auth.*
  script: engineauth.main.application

```

In your `appengine_config.py` add:

```python

config['engineauth.sessions'] = {
    'secret_key': 'CHANGE_TO_A_RANDOM_STRING',
}

config['engineauth.auth'] = {
    'user_model': 'engineauth.models.User',
    'session_backend': 'datastore',
}

# Facebook Authentication
config['engineauth.facebook'] = {
    'client_id': 'CHANGE_TO_FACEBOOK_APP_ID',
    'client_secret': 'CHANGE_TO_FACEBOOK_CLIENT_SECRET',
    'scope': 'email',
}

# Google Plus Authentication
config['engineauth.google'] = {
    'client_id': 'CHANGE_TO_GOOGLE_CLIENT_ID',
    'client_secret': 'CHANGE_TO_GOOGLE_CLIENT_SECRET',
    'api_key': 'CHANGE_TO_GOOGLE_API_KEY',
    'scope': 'https://www.googleapis.com/auth/plus.me',
}

```

