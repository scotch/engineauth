.. _api.engineatuh.models:

Models
======
.. module:: engineauth.models

This module provides a lightweight but flexible session support for webapp2.

.. autoclass:: User
   :members: get_by_auth_id, get_by_auth_token, create,

.. autoclass:: UserToken
   :members: get_key, create, get

.. autoclass:: Unique
   :members: create, create_multi, delete_multi

