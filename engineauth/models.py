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
from engineauth import config
from google.appengine.ext import ndb
from webapp2_extras import securecookie
from webapp2_extras import security



class Error(Exception):
    """Base user exception."""

class DuplicatePropertyError(Error):
    def __init__(self, value):
        self.values = value
        self.msg = u'duplicate properties(s) were found.'

class UserProfile(ndb.Expando):
    """
    ``ndb.Expando`` is used to store the user_info object as well as
    any additional information specific to a strategy.
    """
    _default_indexed = False
    user_info = ndb.JsonProperty(indexed=False, compressed=True)
    credentials = ndb.PickleProperty(indexed=False)

    @classmethod
    def get_or_create(cls, auth_id, user_info, **kwargs):
        """

        """
        profile = cls.get_by_id(auth_id)
        if profile is None:
            profile = cls(id=auth_id)
        profile.user_info = user_info
        profile.populate(**kwargs)
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


class UserEmail(ndb.Model):
    user_id = ndb.StringProperty(indexed=True)
    value = ndb.StringProperty(indexed=True)
    type = ndb.StringProperty(indexed=False)
    primary = ndb.BooleanProperty(default=False, indexed=False)
    verified = ndb.BooleanProperty(default=False, indexed=True)

    @classmethod
    def create(cls, address, user_id, primary=False, verified=False, type=None):
        address = address.lower()
        email = cls.get_by_id(address)
        if email is not None and email.user_id != user_id:
            raise DuplicatePropertyError(['email'])
        email = cls(id=address,
            value=address,
            user_id=user_id,
            primary=primary,
            verified=verified,
            type=type)
        email.put()
        return cls

    @classmethod
    def get_by_user(cls, user_id):
        user_id = str(user_id)
        return cls.query(cls.user_id == user_id).fetch(25)

    @classmethod
    def get_by_emails(cls, addresses):
        assert isinstance(addresses, list), 'Email addresses must be a list'
        if not addresses: return None
        results = cls.query(cls.value.IN(addresses)).fetch(25)
        return results or None



class User(ndb.Expando):
    """Stores user authentication credentials or authorization ids."""
    email_model = UserEmail

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    # ID for third party authentication, e.g. 'google:username'. UNIQUE.
    auth_ids = ndb.StringProperty(repeated=True)
    # primary email address used for
    email = ndb.StringProperty(indexed=False)

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

    def _add_auth_id(self, auth_id):
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

    @classmethod
    def _get_by_auth_id(cls, auth_id):
        """Returns a user object based on a auth_id.

        :param auth_id:
            String representing a unique id for the user. Examples:

            - own:username
            - google:username
        :returns:
            A user object.
        """
        return cls.query(cls.auth_ids == auth_id).get()
    get_by_auth_id = _get_by_auth_id

    def get_emails(self):
        return self.email_model.get_by_user(self.get_id())

    def add_email(self, value, primary=False, verified=False, type=None):
        return self.email_model.create(value, self.get_id(), primary=primary,
            verified=verified, type=type)

#    def _has_email(self, email):
#        """Convenience method that checks if a User has the provided email.
#
#        :param email:
#            A String representing the email to check for
#        :return:
#            True if email is present, else False
#        """
#        for e in self.emails:
#            if e.value == email:
#                return True
#        return False
#
#    def _add_email(self, value, type=u'home', primary=False, verified=False):
#        """Adds and email address to User
#
#        :param value:
#            A String representing the email address
#        :param type:
#            A String representing the type of email.
#            E.g.
#            - 'home'
#            - 'work'
#            - 'other'
#            default: 'home'
#        :param primary:
#            A Boolean indicting weather or not the email should be
#            used for communication
#            default: False
#        :param verified:
#            A Boolean indicting weather or not the email has been
#            verified to be an active address owned by the User
#            default: False
#        :return:
#            User object if the add succeeds
#        :raise:
#            ExistingAccountError is raised if the email address is
#            already in the system user a different User account
#        """
#        if not value:
#            return self
#        value = value.lower()
#        # check if the user has already added the address
#        if self._has_email(value):
#            return self
#            # check for accounts using address
#        if self.__class__().get_by_email(value):
#            raise DuplicatePropertyError(value=['email'])
#        email = self.email_model(value=value, type=type,
#                      primary=primary, verified=verified)
#        self.emails.append(email)
##        self.put()
#        return self
#
#    def _add_emails(self, emails):
#        assert isinstance(emails, list), 'Emails must be a list'
#        for email in emails:
#            pass
#
#    @classmethod
#    def _get_by_emails(cls, emails):
#        """Returns the first User by email address
#
#        :param emails:
#            List of email addresses to search by
#        :return:
#            A User object
#        """
#        assert isinstance(emails, list), 'Emails must be a list'
#        email = emails.lower()
#        return cls.query(cls.emails.value == email).get()

    @classmethod
    def _find_user(cls, auth_id, emails=None):
        """Find User by auth_id and optionally email address

        :param auth_id:
            A String representing a unique id to find the user by
        :param emails:
            Optional, list of email addresses to search by if auth_id
            returns None
        :return: A User by auth_id and optionally email
        """
        user = cls.get_by_auth_id(auth_id)
        if user is None and emails:
            # TODO: email should only be trusted if it is verified.
            assert isinstance(emails, list), 'Emails must be a list'
            address = [e['value'] for e in emails]
            emails = cls.email_model.get_by_emails(address)
            if emails:
                user = cls.get_by_id(int(emails[0].user_id))
        return user

    @classmethod
    def _create_user(cls, auth_ids, **user_values):
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
        if not isinstance(auth_ids, list):
            auth_ids = [auth_ids]
        user_values['auth_ids'] = auth_ids

        for auth_id in user_values['auth_ids']:
            if cls.get_by_auth_id(auth_id):
                raise DuplicatePropertyError(value=['auth_id'])

        user = cls(**user_values)
        user.put()
        return user
    create_user = _create_user

    @classmethod
    def _get_or_create(cls, auth_id, emails, **kwarg):
        assert isinstance(emails, list), 'Emails must be a list'
        user = cls._find_user(auth_id, emails)
#        if user and emails is not None:
#            user._add_emails(emails)
        if user is None:
            user = cls._create_user(auth_id, **kwarg)
        return user

    @classmethod
    def get_or_create_by_profile(cls, profile):
        assert isinstance(profile, UserProfile), \
            'You must pass an instance of type engineauth.models.UserProfile.'
        emails = profile.user_info.get('info').get('emails') or []
        return cls._get_or_create(profile.key.id(), emails)


    def add_profile(self, profile):
        assert isinstance(profile, UserProfile),\
            'You must pass an instance of type engineauth.models.UserProfile.'
        return self._add_auth_id(profile.key.id())


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
        engineauth_config = config.load_config()
        return securecookie.SecureCookieSerializer(engineauth_config['secret_key'])

    def hash(self):
        """
        Creates a unique hash from the session.
        This will be used to check for session changes.
        :return: A unique hash for the session
        """
        dataStr = repr(self.data)
        return "{}.{}.{}.{}.{}".format(self.session_id, self.user_id,
                                       str(self.updated), hash(dataStr),
                                       len(dataStr))

    def serialize(self):
        values = self.to_dict(include=['session_id', 'user_id'])
        return self._serializer().serialize('_eauth', values)

    @classmethod
    def deserialize(cls, value):
        return cls._serializer().deserialize('_eauth', value)

    @classmethod
    def get_by_value(cls, value):
        v = cls.deserialize(value)
        if v:
            return cls.get_by_sid(v.get('session_id'))
        return None

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
        # for testing we want to be able to pass a value for now.
        now = now or datetime.datetime.now()
        dtd = now + datetime.timedelta(-days_ago)
        for s in cls.query(cls.updated < dtd).fetch():
            s.key.delete()
