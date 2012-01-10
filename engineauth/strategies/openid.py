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
from __future__ import absolute_import
# TODO: WORK IN PROGRESS. DO NOT USE

import cPickle as pickle
from engineauth.strategies.base import BaseStrategy
from google.appengine.api import memcache
from openid.consumer.consumer import Consumer
from openid.extensions import sreg
from openid.extensions import ax
from openid.association import Association as OpenIDAssociation
from openid.store import interface
from openid.store import nonce

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'
MEMCACHE_NAMESPACE = 'eauth'


class AppEngineStore(interface.OpenIDStore):
    def getAssociationKeys(self, server_url, handle):
        return ("assoc:%s" % (server_url,),
                "assoc:%s:%s" % (server_url, handle))

    def storeAssociation(self, server_url, association):
        data = association.serialize()
        key1, key2 = self.getAssociationKeys(server_url, association.handle)
        memcache.set_multi({key1: data, key2: data},
            namespace=MEMCACHE_NAMESPACE)

    def getAssociation(self, server_url, handle=None):
        key1, key2 = self.getAssociationKeys(server_url, handle)
        if handle:
            results = memcache.get_multi([key1, key2], namespace=MEMCACHE_NAMESPACE)
        else:
            results = {key1: memcache.get(key1, namespace=MEMCACHE_NAMESPACE)}
        data = results.get(key2) or results.get(key1)
        if data:
            return OpenIDAssociation.deserialize(data)
        else:
            return None

    def removeAssociation(self, server_url, handle):
        key1, key2 = self.getAssociationKeys(server_url, handle)
        return memcache.delete(key2) == 2

    def useNonce(self, server_url, timestamp, salt):
        nonce_key = "nonce:%s:%s" % (server_url, salt)
        expires_at = timestamp + nonce.SKEW
        return memcache.add(nonce_key, None, time=expires_at,
            namespace=MEMCACHE_NAMESPACE)

class Flow(object):
    """Base class for all Flow objects."""
    pass

# list of attributes to request via Simple Registration
OPENID_SREG_ATTRS = ['nickname', 'email']

# dict of uris => attributes to request via Attribute Exchange
OPENID_AX_ATTRS = {
    'http://axschema.org/contact/email':        'email',
    'http://axschema.org/namePerson/friendly':  'nickname',
    'http://axschema.org/namePerson/first':     'firstname',
    'http://axschema.org/namePerson/last':      'lastname',
    }


class FlowOpenID(Flow):
    """Does the OpenID Dance.
    """

    def __init__(self, session, store, host_url, **kwargs):
        self.session = session
        self.store = store
        self.host_url = host_url

    def step1_get_authorize_url(self, openid_url, callback_url):
        """Returns a URI to redirect to the provider.
        """
        consumer = Consumer(self.session, self.store)
        # if consumer discovery or authentication fails, show error page
        try:
            request = consumer.begin(openid_url)
        except Exception, e:
            raise e
        # TODO: Support custom specification of extensions
        # TODO: Don't ask for data we already have, perhaps?
        # use Simple Registration if available
        request.addExtension(sreg.SRegRequest(required=OPENID_SREG_ATTRS))
        # or Atribute Exchange if available
        ax_request = ax.FetchRequest()
        for attruri in OPENID_AX_ATTRS:
            ax_request.add(ax.AttrInfo(attruri, required=True,
                alias=OPENID_AX_ATTRS[attruri]))
        request.addExtension(ax_request)
        return request.redirectURL(self.host_url, callback_url)

    def step2_exchange(self, verifier):
        pass

class OpenIDStrategy(BaseStrategy):

    def user_info(self, req):
        pass

    def start(self, req):
        openid_url = req.GET.get('openid_url')
        if not openid_url:
            return self.raise_error('opeinid_url not provided')
        try:
            authorize_url = req.flow.step1_get_authorize_url(
                openid_url, self.callback_uri)
            req.session.data[self.session_key]['flow'] = pickle.dumps(req.flow)
            return authorize_url
        except Exception, e:
            raise e

    def callback(self, req):
        user_info = self.user_info(req)
        profile = self.get_or_create_profile(
            auth_id=user_info['uid'],
            user_info=user_info)
        req.load_user_by_profile(profile)
        return req.get_redirect_uri()

    def handle_request(self, req):
        self.callback_uri = '{0}{1}/{2}/callback'.format(req.host_url,
            req.config['base_uri'], req.provider)
        self.session_key = '_auth_strategy:{0}'.format(req.provider)
        req.session.data[self.session_key] = {
            'session': {},
            'flow': ''
        }
        req.flow = FlowOpenID(
            session=req.session.data[self.session_key]['session'],
            store=AppEngineStore,
            host_url=req.host_url,
        )
        if not req.provider_params:
            return self.start(req)
        else:
            return self.callback(req)