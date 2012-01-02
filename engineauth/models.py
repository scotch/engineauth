# -*- coding: utf-8 -*-
"""
    engineauth.models
    ====================================

    Auth related models.

    :copyright: 2011 by Rodrigo Moraes.
    :license: Apache Sotware License, see LICENSE for details.

    :copyright: 2011 by tipfy.org.
    :license: Apache Sotware License, see LICENSE for details.
"""
import time

from appengine_config import engineauth
import ndb
from webapp2_extras import securecookie
from webapp2_extras import security



class Error(Exception):
    """Base user exception."""

class DuplicatePropertyError(Error):
    def __init__(self, value):
        self.values = value
        self.msg = u'duplicate properties(s) were found.'


class Email(ndb.Model):
    value = ndb.StringProperty(indexed=True)
    type = ndb.StringProperty(indexed=False)
    primary = ndb.BooleanProperty(default=False, indexed=False)
    verified = ndb.BooleanProperty(default=False, indexed=True)

class Profile(ndb.Expando):
    _default_indexed = False
    user_info = ndb.JsonProperty(indexed=False, compressed=True)
    credentials = ndb.PickleProperty(indexed=False)

    @classmethod
    def get_or_create(cls, auth_id, user_info, **kwarg):
        profile = cls.get_by_id(auth_id)
        if profile is None:
            profile = cls(id=auth_id)
        profile.user_info = user_info
        profile.populate(**kwarg)
        profile.put()
        return profile


class UserToken(ndb.Model):
    """Stores validation tokens for users."""

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    user = ndb.StringProperty(required=True, indexed=False)
    subject = ndb.StringProperty(required=True)
    token = ndb.StringProperty(required=True)

    @classmethod
    def get_key(cls, user, subject, token):
        """Returns a token key.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param token:
            Randomly generated token.
        :returns:
            ``model.Key`` containing a string id in the following format:
            ``{user_id}.{subject}.{token}``
        """
        return ndb.Key(cls, '%s.%s.%s' % (str(user), subject, token))

    @classmethod
    def create(cls, user, subject, token=None):
        """Creates a new token for the given user.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param token:
            Optionally an existing token may be provided.
            If None, a random token will be generated.
        :returns:
            The newly created :class:`UserToken`.
        """
        user = str(user)
        token = token or security.generate_random_string(entropy=128)
        key = cls.get_key(user, subject, token)
        entity = cls(key=key, user=user, subject=subject, token=token)
        entity.put()
        return entity

    @classmethod
    def get(cls, user=None, subject=None, token=None):
        """Fetches a user token.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param token:
            The existing token needing verified.
        :returns:
            A :class:`UserToken` or None if the token does not exist.
        """
        if user and subject and token:
            return cls.get_key(user, subject, token).get()

        assert subject and token, \
            u'subject and token must be provided to UserToken.get().'
        return cls.query(cls.subject == subject, cls.token == token).get()


class User(ndb.Expando):
    """Stores user authentication credentials or authorization ids."""

    #: The model used to ensure uniqueness.
#    unique_model = Unique
    #: The model used to store tokens.
    token_model = UserToken
    email_model = Email
    profile_model = Profile

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    # ID for third party authentication, e.g. 'google:username'. UNIQUE.
    auth_ids = ndb.StringProperty(repeated=True)
    emails = ndb.StructuredProperty(Email, repeated=True)

    # Hashed password. Not required because third party authentication
    # doesn't use password.
#    password = ndb.StringProperty()
    authenticated = ndb.BooleanProperty(default=False)

    def get_id(self):
        """Returns this user's unique ID, which can be an integer or string."""
        return str(self.key.id())
    
    @staticmethod
    def generate_auth_id(provider, uid, subprovider=None):
        """Standardized generator for auth_ids

        :param provider:
            A String representing the provider of the id.
            E.g.
            - 'google'
            - 'facebook'
            - 'appengine_openid'
            - 'twitter'
        :param uid:
            A String representing a unique id generated by the Provider.
            I.e. a user id.
        :param subprovider:
            An Optional String representing a more granular subdivision of a provider.
            i.e. a appengine_openid has subproviders for Google, Yahoo, AOL etc.
        :return:
            A concatenated String in the following form:
            '{provider}#{subprovider}:{uid}'
            E.g.
            - 'facebook:1111111111'
            - 'twitter:1111111111'
            - 'appengine_google#yahoo:1111111111'
            - 'appengine_google#google:1111111111'
        """
        if subprovider is not None:
            provider = '{0}#{1}'.format(provider, subprovider)
        return '{0}:{1}'.format(provider, uid)

    def _has_email(self, email):
        """Convenience method that checks if a User has the provided email.

        :param email:
            A String representing the email to check for
        :return:
            True if email is present, else False
        """
        for e in self.emails:
            if e.value == email:
                return True
        return False

    def add_auth_id(self, auth_id):
        """A helper method to add additional auth ids to a User

        :param auth_id:
            String representing a unique id for the user. Examples:

            - own:username
            - google:username
        :returns:
            A tuple (boolean, info). The boolean indicates if the user
            was saved. If creation succeeds, ``info`` is the user entity;
            otherwise it is a list of duplicated unique properties that
            caused creation to fail.
        """
        # If the auth_id is already in the list return True
        if auth_id in self.auth_ids:
            return self
        if self.__class__.get_by_auth_id(auth_id):
            raise DuplicatePropertyError(value=['auth_id'])
        else:
            self.auth_ids.append(auth_id)
            self.put()
            return self

    def add_email(self, value, type=u'home', primary=False, verified=False):
        """Adds and email address to User

        :param value:
            A String representing the email address
        :param type:
            A String representing the type of email.
            E.g.
            - 'home'
            - 'work'
            - 'other'
            default: 'home'
        :param primary:
            A Boolean indicting weather or not the email should be
            used for communication
            default: False
        :param verified:
            A Boolean indicting weather or not the email has been
            verified to be an active address owned by the User
            default: False
        :return:
            User object if the add succeeds
        :raise:
            ExistingAccountError is raised if the email address is
            already in the system user a different User account
        """
        if not value:
            return self
        value = value.lower()
        # check if the user has already added the address
        if self._has_email(value):
            return self
            # check for accounts using address
        if self.__class__().get_by_email(value):
            raise DuplicatePropertyError(value=['email'])
        email = self.email_model(value=value, type=type,
                      primary=primary, verified=verified)
        self.emails.append(email)
        self.put()
        return self

    @classmethod
    def get_by_auth_id(cls, auth_id):
        """Returns a user object based on a auth_id.

        :param auth_id:
            String representing a unique id for the user. Examples:

            - own:username
            - google:username
        :returns:
            A user object.
        """
        return cls.query(cls.auth_ids == auth_id).get()

    @classmethod
    def get_by_auth_token(cls, user_id, token):
        """Returns a user object based on a user ID and token.

        :param user_id:
            The user_id of the requesting user.
        :param token:
            The token string to be verified.
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        token_key = cls.token_model.get_key(user_id, 'auth', token)
        user_key = ndb.Key(cls, user_id)
        # Use get_multi() to save a RPC call.
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp

        return None, None

    @classmethod
    def get_by_email(cls, email):
        """Returns the first User by email address

        :param email:
            String representing the email address to search by
        :return:
            A User object
        """
        email = email.lower()
        return cls.query(cls.emails.value == email).get()

    @classmethod
    def create_token(cls, user_id, token_type='auth'):
        """Creates a new token for a given user ID and token type.

        :param user_id:
            User unique ID.
        :param token_type:
            A String representing the type of taken.
            Default: 'auth'
        :returns:
            A string with the authorization token.
        """
        return cls.token_model.create(user_id, token_type).token

    @classmethod
    def validate_token(cls, user_id, token, token_type='auth'):
        """Checks for existence of a token, given user_id, token and token_type.

        :param user_id:
            User unique ID.
        :param token_type:
            A String representing the type of taken.
            E.g.
            - 'auth'
            - 'signup'
            Default: 'auth'
        :param token:
            The token string to be validated.
        :returns:
            A :class:`UserToken` or None if the token does not exist.
        """
        return cls.token_model.get(user=user_id, subject=token_type,
                                   token=token) is not None

    @classmethod
    def delete_token(cls, user_id, token, token_type='auth'):
        """Deletes a given token.

        :param user_id:
            User unique ID.
        :param token_type:
            A String representing the type of taken.
            Default: 'auth'
        :param token:
            A string with the authorization token.
        """
        cls.token_model.get_key(user_id, token_type, token).delete()


    @classmethod
    def find_user(cls, auth_id, email=None):
        """Find User by auth_id and optionally email address

        :param auth_id:
            A String representing a unique id to find the user by
        :param email:
            Optional, an email address to search by if auth_id
            returns None
        :return: A User by auth_id and optionally email
        """
        user = cls.get_by_auth_id(auth_id)
        if user is None and email:
            user = cls.get_by_email(email)
        return user

    @classmethod
    def create_user(cls, auth_id, **user_values):
        """Creates a new user.

        :param auth_id:
            A string that is unique to the user. Users may have multiple
            auth ids. Example auth ids:

            - own:username
            - own:email@example.com
            - google:username
            - yahoo:username

            The value of `auth_id` must be unique.
        :param user_values:
            Keyword arguments to create a new user entity. Since the model is
            an ``Expando``, any provided custom properties will be saved.
            To hash a plain password, pass a keyword ``password_raw``.
        :returns:
            A tuple (boolean, info). The boolean indicates if the user
            was created. If creation succeeds, ``info`` is the user entity;
            otherwise it is a list of duplicated unique properties that
            caused creation to fail.
        """

        assert not isinstance(auth_id, list), \
            'Creating a user with multiple auth_ids is not allowed, ' \
            'please provide a single auth_id.'
        email = user_values.get('emails', None)
        if email:
            user_values['emails'] = [cls.email_model(value=email)]
        user_values['auth_ids'] = [auth_id]
        if cls.get_by_auth_id(auth_id):
            raise DuplicatePropertyError(value=['auth_id'])
        user = cls(**user_values)
        user.put()
        return user

    @classmethod
    def get_or_create(cls, auth_id, email, **kwarg):
        user = cls.find_user(auth_id, email)
        if user and email is not None:
            user.add_email(email)
        if user is None:
            user = cls.create_user(auth_id, emails=email)
        return user


class Session(ndb.Model):
    session_id = ndb.StringProperty()
    user_id = ndb.StringProperty()
    updated = ndb.DateTimeProperty(auto_now=True)
    data = ndb.PickleProperty(compressed=True, default={})

    @staticmethod
    def _generate_sid():
        return security.generate_random_string(entropy=128)

    @staticmethod
    def _serializer():
        return securecookie.SecureCookieSerializer(engineauth['secret_key'])

    def hash(self):
        """
        Creates a unique hash from the session.
        This will be used to check for session changes.
        :return: A unique hash for the session
        """
        return hash(str(self))

    def serialize(self):
        values = self.to_dict(include=['session_id', 'user_id'])
        return self._serializer().serialize('_eauth', values)

    @classmethod
    def deserialize(cls, value):
        return cls._serializer().deserialize('_eauth', value)

    @classmethod
    def get_by_value(cls, value):
        v = cls.deserialize(value)
        sid = v.get('session_id')
        return cls.get_by_sid(sid) if sid else None

    @classmethod
    def get_by_sid(cls, sid):
        return cls.get_by_id(sid)

    @classmethod
    def upgrade_to_user_session(cls, session_id, user_id):
        old_session = cls.get_by_sid(session_id)
        new_session = cls.create(user_id=user_id, data=old_session.data)
        old_session.key.delete()
        return new_session

    @classmethod
    def get_by_user_id(cls, user_id):
        # TODO: make sure that the user doesn't have multiple sessions
        user_id = str(user_id)
        return cls.query(cls.user_id == user_id).get()

    @classmethod
    def create(cls, user_id=None, **kwargs):
        if user_id is None:
            session_id = cls._generate_sid()
        else:
            session_id = user_id = str(user_id)
        session = cls(id=session_id, session_id=session_id,
            user_id=user_id, **kwargs)
        session.put()
        return session

    @classmethod
    def remove_inactive(cls, days_ago=30, now=None):
        import datetime
        if now is None:
            # for testing we want to be able to pass a value for now.
            now = datetime.datetime.now()
        dtd = now + datetime.timedelta(-days_ago)
        for s in cls.query(cls.updated < dtd).fetch():
            s.key.delete()