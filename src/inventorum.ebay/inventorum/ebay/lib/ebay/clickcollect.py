# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from ebaysdk.response import Response
from ebaysdk.utils import dict2xml
import requests

class EbayClickCollect(object):
    base_url = 'https://api.ebay.com/selling/inventory/v1/'

    _list_nodes = [
        'addinventoryrequest.locations.location',

    ]
    def __init__(self, token):
        """
        :type token: inventorum.ebay.lib.ebay.data.authorization.EbayToken
        """
        self.token = token

    def _get_default_headers(self):
        return {
            'Authorization': 'TOKEN {token}'.format(self.token.value),
            'Content-Type': 'application/xml'
        }

    def _make_request(self, method, url, data=None, params=None, headers=None):
        url = '{0}{1}'.format(self.base_url, url)
        default_headers = self._get_default_headers()
        if headers:
            default_headers.update(**headers)

        request_method = getattr(requests, method)
        response = request_method(url, data=data, params=params, headers=default_headers)


        self.response = Response(self.response,
                                 verb=self.verb,
                                 list_nodes=self._list_nodes,
                                 datetime_nodes=self.datetime_nodes,
                                 parse_response=True)


    def _build_request_data(self, verb, data, verb_attrs):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<{verb}Request>".format(verb=verb)
        xml += dict2xml(data)
        xml += "</{verb}Request>".format(verb=verb)
        return xml
