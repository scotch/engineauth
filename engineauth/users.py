#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import urllib
import urlparse

from google.appengine.ext import db


OPENID_PATH_PREFIX = '/_openid/'
OPENID_LOGIN_PATH = OPENID_PATH_PREFIX + 'login'
OPENID_FINISH_PATH = OPENID_PATH_PREFIX + 'finish'
OPENID_LOGOUT_PATH = OPENID_PATH_PREFIX + 'logout'
OPENID_STATIC_PATH = OPENID_PATH_PREFIX + 'static/(.*)\.([^.]+)'


_current_user = None


class UserInfo(db.Expando):
    """Internal user information for an OpenID-authenticated user."""

    server_url = db.StringProperty()
    nickname = db.StringProperty(indexed=False)
    email = db.StringProperty()

    @property
    def identity_url(self):
        """Returns the user's OpenID identity URL."""
        return self.key().name()

    @classmethod
    def kind(cls):
        return "AeoidUser"

    @classmethod
    def get_by_identity_url(cls, identity_url):
        """Fetches a user by their OpenID URL."""
        return cls.get_by_key_name(identity_url)

    @classmethod
    def update_or_insert(cls, identity_url, **kwargs):
        """Creates an entity, or updates it if it already exists."""
        def _tx():
            user = cls.get_by_identity_url(identity_url)
            if user:
                for k, v in kwargs.iteritems():
                    setattr(user, k, v)
            else:
                user = cls(key_name=identity_url, **kwargs)
            user.put()
            return user
        return db.run_in_transaction(_tx)


class User(object):
    """A user.

    We provide the email address, nickname, and id for a user.

    Note that unlike the native App Engine Users API, nicknames and email
    addresses are not guaranteed to be unique, and because they are entered by
    the user, the email is not guaranteed to be valid and owned by the user in
    question, either - so perform your own validation if you're unsure!
    """

    def __init__(self, identity_url, _from_model_key=None, _from_model=None,
                 **kwargs):
        """Constructor.

        Args:
          identity_url: The OpenID URL of the user. Required to construct a User
            object.
          email: The user's email address.
          nickname: The user's nickname.
        """
        if _from_model_key:
            self._user_info = _from_model
            if isinstance(_from_model_key, basestring):
                self._user_info_key = db.Key(_from_model_key)
            else:
                self._user_info_key = _from_model_key
        else:
            self._user_info = UserInfo.update_or_insert(identity_url, **kwargs)
            self._user_info_key = self._user_info.key()

    def user_info(self):
        """Returns the internal user_info entity for this user."""
        if not self._user_info:
            self._user_info = db.get(self._user_info_key)
        return self._user_info

    def nickname(self):
        """Return this user's nickname.

        The nickname is a human readable identifier for this user, chosen by them
        when they first logged in. It may not be unique!
        """
        return self.user_info().nickname

    def email(self):
        """Return this user's email address.

        Unlike the native Users API, aeoid does NOT validate emails, so the address
        provided is not guaranteed to be unique, or even owned by the user in
        question. If in doubt, perform your own validation!
        """
        return self.user_info().email

    def user_id(self):
        """Return a permanent unique identifying string.

        In aeoid, the string returned is the user's OpenID URL.
        """
        return self._user_info_key.name()


def _get_current_url():
    if os.environ.get('HTTPS') == 'on':
        url = 'https://'
    else:
        url = 'http://'
    url += os.environ['HTTP_HOST']
    url += urllib.quote(os.environ['SCRIPT_NAME'])
    url += urllib.quote(os.environ['PATH_INFO'])
    if os.environ.get('QUERY_STRING'):
        url += '?' + os.environ['QUERY_STRING']


def _create_redirect_url(target, continue_url):
    current_url = _get_current_url()
    # Convert dest_url to an absolute URL
    continue_url = urlparse.urljoin(current_url, continue_url)
    redirect_url = '%s?continue=%s' % (target, urllib.quote(continue_url))
    # Convert the login URL to an absolute URL
    redirect_url = urlparse.urljoin(current_url, redirect_url)
    return redirect_url


def create_login_url(dest_url):
    """Returns a URL that, when visited, prompts the user to sign in using OpenID.

    Args:
      dest_url: str: A full URL or relative path to redirect to after logging in.
    Returns:
      str: A URL to redirect the user to for login.
    """
    return _create_redirect_url(OPENID_LOGIN_PATH, dest_url)


def create_logout_url(dest_url):
    """Returns a URL that, when visited, logs the user out.

    Args:
      dest_url: str: A full URL or relative path to redirect to after logging out.
    Returns:
      str: A URL to redirect the user to for logout.
    """
    return _create_redirect_url(OPENID_LOGOUT_PATH, dest_url)


def get_current_user():
    """Returns the currently logged in user, or None if no user is logged in."""
    global _current_user

    if not _current_user and 'aeoid.user' in os.environ:
        _current_user = User(None, _from_model_key=os.environ['aeoid.user'])
    return _current_user


def is_current_user_admin():
    """Returns True if the current user is signed in and is an administrator."""
    # TODO: Implement
    return False


class UserProperty(db.Property):
    """A user with an OpenID account."""

    def __init__(self,
                 verbose_name=None,
                 name=None,
                 required=False,
                 validator=None,
                 choices=None,
                 auto_current_user=False,
                 auto_current_user_add=False,
                 indexed=True):
        """Initializes this Property with the given options.

        If auto_current_user is True, the property value is set to the currently
        signed-in user whenever the model instance is stored in the datastore,
        overwriting the property's previous value. This is useful for tracking which
        user modifies a model instance.

        If auto_current_user_add is True, the property value is set to the currently
        signed-in user the first time the model instance is stored in the datastore,
        unless the property has already been assigned a value. This is useful for
        tracking which user creates a model instance, which may not be the same user
        that modifies it later.

        UserProperty does not accept a default value. Default values are set when
        the model class is first imported, and with import caching may not be the
        currently signed-in user.

        Args:
          verbose_name: User friendly name of property.
          name: Storage name for property.
          required: Whether property is required.
          validator: User provided method used for validation.
          choices: User provided set of valid property values.
          auto_current_user: If true, the value is set to the current user each time
            the entity is written to the datastore.
          auto_current_user_add: If true, the value is set to the current user the
            first time the entity is written to the datastore.
          indexed: Whether property is indexed.
        """
        super(UserProperty, self).__init__(verbose_name, name, required=required,
            validator=validator, choices=choices,
            indexed=indexed)
        self.auto_current_user = auto_current_user
        self.auto_current_user_add = auto_current_user_add

    def validate(self, value):
        """Validate user.

        Returns:
          A valid value.

        Raises:
          BadValueError if property is not an instance of 'User'.
        """
        if value is not None and not isinstance(value, User):
            raise BadValueError('Property %s must be a User' % self.name)
        return value

    def default_value(self):
        """Default value for user.

        Returns:
          Value of users.get_current_user() if auto_current_user or
          auto_current_user_add is set; else None.
        """
        if self.auto_current_user or self.auto_current_user_add:
            return get_current_user()
        return None

    def get_value_for_datastore(self, model_instance):
        """Get value from property to send to datastore.

        Returns:
          A db.Key to store.
        """
        if self.auto_current_user:
            user = get_current_user()
        else:
            user = super(UserProperty, self).get_value_for_datastore(model_instance)
        if user:
            return user._user_info_key

    def make_value_from_datastore(self, value):
        """Construct a User object from the datastore representation.

        Args:
          value: Value retrieved from the datastore entity.
        Returns:
          A User object.
        """
        if value is None:
            return None
        else:
            return User(None, _from_model_key=value)
