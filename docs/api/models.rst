.. _api.engineatuh.models:

Models
======
.. module:: engineauth.models

This module provides the ndb models used in EngineAuth.

.. autoclass:: User
   :members: get_by_auth_id, create_user,

.. autoclass:: UserProfile
   :members: get_or_create

.. autoclass:: UserToken
   :members: get_key, create, get

.. autoclass:: UserEmail
   :members: create

.. autoclass:: Session
   :members: create


