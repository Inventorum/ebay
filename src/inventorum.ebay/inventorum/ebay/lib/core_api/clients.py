# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import json
import logging
from collections import defaultdict
from pprint import pprint

import requests
from django.conf import settings

from inventorum.ebay.lib.core_api import CoreChannel
from inventorum.ebay.lib.core_api.models import CoreProductDeserializer, CoreInfoDeserializer, \
    CoreProductDeltaDeserializer, CoreOrder, CoreDeltaReturn
from inventorum.ebay.lib.core_api.pager import Pager
from inventorum.util.django.middlewares import get_current_request_id
from inventorum.ebay.apps.inventory.serializers import QuantityCoreApiResponseDeserializer

log = logging.getLogger(__name__)


class CoreAPIClientException(Exception):
    pass


class CoreAPIClient(object):
    API_VERSION = 10

    @property
    def default_headers(self):
        """
        :return: The default headers that are sent with every request unless explicitly overwritten
        :rtype: dict
        """
        return {
            "User-Agent": "inv-ebay/{version}".format(version=settings.VERSION),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Version": self.API_VERSION,
            "X-Rid": get_current_request_id()
        }

    @classmethod
    def url_for(cls, path):
        """
        Returns the full core api url for the given relative path

        :param path: Relative core api path
        :return: Full core api url

        :type path: str | unicode
        :rtype: unicode
        """
        if not path.startswith("/"):
            path = "/{path}".format(path=path)

        protocol = 'https' if settings.INV_CORE_API_SECURE else 'http'
        return "{protocol}://{host}{path}".format(protocol=protocol, host=settings.INV_CORE_API_HOST, path=path)

    def get(self, path, params=None, custom_headers=None):
        """
        Performs a get request to the given core api path with the given params/headers

        :param path: The core api request path
        :param params: Optional URL params
        :param custom_headers: Optional custom HTTP headers (default header can be overwritten)
        :return: The HTTP response

        :type path: str | unicode
        :type params: dict
        :type custom_headers: dict

        :rtype: requests.models.Response

        :raises requests.exceptions.RequestException
        """
        if custom_headers is None:
            custom_headers = {}

        headers = self.default_headers
        headers.update(custom_headers)

        response = requests.get(self.url_for(path), params=params, headers=headers)
        if not response.ok:
            response.raise_for_status()

        return response

    def post(self, path, data=None, params=None, custom_headers=None):
        """
        Performs a post request to the given core api path with the given params/headers

        :param path: The core api request path
        :param data: Payload
        :param params: Optional URL params
        :param custom_headers: Optional custom HTTP headers (default header can be overwritten)
        :return: The HTTP response

        :type path: str | unicode
        :type data: dict
        :type params: dict
        :type custom_headers: dict

        :rtype: requests.models.Response

        :raises requests.exceptions.RequestException
        """
        params = params or {}
        custom_headers = custom_headers or {}
        data = data or {}

        headers = self.default_headers
        headers.update(custom_headers)

        response = requests.post(self.url_for(path), json=data, params=params, headers=headers)

        if not response.ok:
            log.error(dict(url=self.url_for(path), params=params, headers=headers, json=data))
            log.error(response.content)
            response.raise_for_status()

        return response

    def put(self, path, data=None, params=None, custom_headers=None):
        """
        Performs a post request to the given core api path with the given data and params/headers

        :param path: The core api request path
        :param data: The payload sent in the request body (will be json encoded)
        :param params: Optional URL params
        :param custom_headers: Optional custom HTTP headers (default header can be overwritten)
        :return: The HTTP response

        :type path: str | unicode
        :type data:
        :type params: dict
        :type custom_headers: dict

        :rtype: requests.models.Response

        :raises requests.exceptions.RequestException
        """
        headers = self._get_request_headers(custom_headers)

        response = requests.put(self.url_for(path), json=data, params=params, headers=headers)

        if not response.ok:
            response.raise_for_status()

        return response

    def delete(self, path, params=None, custom_headers=None):
        """
        Performs a delete request to the given core api path with the given params/headers

        :param path: The core api request path
        :param params: Optional URL params
        :param custom_headers: Optional custom HTTP headers (default header can be overwritten)
        :return: The HTTP response

        :type path: str | unicode
        :type data:
        :type params: dict
        :type custom_headers: dict

        :rtype: requests.models.Response

        :raises requests.exceptions.RequestException
        """
        headers = self._get_request_headers(custom_headers)

        response = requests.delete(self.url_for(path), params=params, headers=headers)

        if not response.ok:
            response.raise_for_status()

        return response

    def paginated_get(self, path, limit_per_page, params=None, custom_headers=None):
        """
        Returns a pager that paginates the given paginated core api path with the given limit per page.

        *Note*: The pager immediately requests the first page to initiate the pager accordingly

        :param path: The core api request path
        :param limit_per_page: The limit of items per page
        :param params: Optional URL params
        :param custom_headers: Optional custom HTTP headers (default header can be overwritten)
        :return: The pager instance

        :type path: str | unicode
        :type limit_per_page: int
        :type params: dict
        :type custom_headers: dict

        :rtype: Pager

        :raises requests.exceptions.RequestException, inventorum.ebay.apps.core_api.pager.PagerException
        """
        return Pager(client=self, path=path, limit_per_page=limit_per_page,
                     params=params, custom_headers=custom_headers)

    def _encode_request_data(self, payload):
        return json.dumps(payload)

    def _get_request_headers(self, custom_headers=None):
        if custom_headers is None:
            custom_headers = {}

        headers = self.default_headers
        headers.update(custom_headers)

        return headers

    def _encode_datetime(self, dt):
        """
        :type dt: datetime.datetime
        """
        return dt.replace(microsecond=0).isoformat()

    # This attributed is shared between objects, and that's ok for a cache.
    _product_attribute_translations_cache = defaultdict(dict)

    def get_product_attribute_translations(self, language='de'):
        """Return a dict containing attribute names and their translations to the specified `language`.

        :rtype: dict
        """
        translations = self._product_attribute_translations_cache[language]
        if not translations:
            response = self.get('/api/public/info/attributes/', custom_headers={'Accept-Language': language})
            translations.update(response.json())

        # Return a copy so if someone modifies it, it does not affect the cache.
        return dict(translations)


class UserScopedCoreAPIClient(CoreAPIClient):
    def __init__(self, user_id, account_id):
        """
        :param user_id: The global inventorum user id that is used for the api scope
        :param account_id: The global inventorum account id that is used for the api scope

        :type user_id: int
        :type account_id: int
        """
        self.account_id = account_id
        self.user_id = user_id

    @property
    def default_headers(self):
        """
        :return: The default headers that are sent with every request unless explicitly overwritten
        :rtype: dict
        """
        default_headers = super(UserScopedCoreAPIClient, self).default_headers

        default_headers.update({
            "X-Inv-User": unicode(self.user_id),
            "X-Inv-Account": unicode(self.account_id)
        })
        return default_headers

    def get_product(self, product_id):
        """
        :param product_id: The global inventorum product id

        :type product_id: int
        :rtype: inventorum.ebay.apps.core_api.models.CoreProduct
        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        response = self.get("/api/products/{product_id}/".format(product_id=product_id))
        json = response.json()
        log.debug('Got json from /api/products/%s/: %s', product_id, json)
        serializer = CoreProductDeserializer(data=json)
        return serializer.build()

    def get_account_info(self):
        """
        :rtype: inventorum.ebay.apps.core_api.models.CoreInfo
        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        response = self.get("/api/info/")
        json = response.json()
        serializer = CoreInfoDeserializer(data=json)
        return serializer.build()

    def get_quantity_info(self, product_ids):
        """
        Ask core API about current quantity of products.

        :type product_ids list of int
        :rtype: list of inventorum.ebay.apps.inventory.models.CoreQuantity
        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        response = self.get('/api/products/quantity/', params={'id': product_ids})
        json = response.json()
        serializer = QuantityCoreApiResponseDeserializer(data=json, many=True)
        return serializer.build()

    def get_paginated_product_delta_modified(self, start_date, limit_per_page=100):
        """
        :type start_date: datetime.datetime
        :type limit_per_page: int

        :rtype: collections.Iterable[list of inventorum.ebay.apps.core_api.models.CoreProductDelta]
        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        # verbose = ebay meta attributes will be included in the response
        params = {
            "verbose": True,
            "start_date": self._encode_datetime(start_date)
        }

        pager = self.paginated_get("/api/products/delta/modified/", limit_per_page=limit_per_page, params=params)
        for page in pager.pages:
            serializer = CoreProductDeltaDeserializer(data=page.data, many=True)
            yield serializer.build()

    def get_paginated_product_delta_deleted(self, start_date, limit_per_page=10000):
        """
        :type start_date: datetime.datetime
        :type limit_per_page: int

        :rtype: collections.Iterable[list of int]
        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        params = {
            "start_date": self._encode_datetime(start_date)
        }
        pager = self.paginated_get("/api/products/delta/deleted/", limit_per_page=limit_per_page, params=params)
        for page in pager.pages:
            yield page.data

    def get_paginated_orders_delta(self, start_date, limit_per_page=100):
        """
        :type start_date: datetime.datetime
        :type limit_per_page: int

        :rtype: collections.Iterable[list of ???]
        :raises requests.exceptions.RequestError
                rest_framework.exceptions.ValidationError
        """
        params = {
            "channel": CoreChannel.EBAY,
            "start_date": self._encode_datetime(start_date)
        }

        pager = self.paginated_get("/api/orders/delta/", limit_per_page=limit_per_page, params=params)
        for page in pager.pages:
            serializer = CoreOrder.Serializer(data=page.data, many=True)
            yield serializer.build()

    def post_product_publishing_state(self, inv_product_id, state, details):
        """
        Send state about publishing product to Inventorum api. Returns nothing, in case of failure raises
        :param inv_product_id: Product id of inventorum database
        :param state: State of publishing (check PublishStates)
        :param details: Additional details (optional)

        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        data = {
            'channel': 'ebay',
            'state': state,
            'details': details
        }
        return self.post('/api/products/{}/state/'.format(inv_product_id), data=data)

    def create_order(self, data):
        """
        Tries to create an order with the given data

        :type data: dict

        :returns: The core order
        :rtype: inventorum.ebay.lib.core_api.models.CoreOrder

        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        response = self.post('/api/orders/', data=data)
        json = response.json()

        serializer = CoreOrder.Serializer(data=json)
        return serializer.build()

    @property
    def returns(self):
        """
        :rtype: CoreReturnsClient
        """
        return CoreReturnsClient(core_client=self)


class CoreReturnsClient(object):
    def __init__(self, core_client):
        """
        :type core_client: UserScopedCoreAPIClient
        """
        self.core_client = core_client

    def create(self, order_id, data):
        """
        Tries to create a return with the given data

        :type order_id: int
        :type data: dict

        :returns: The inventorum return id
        :rtype: int

        :raises requests.exceptions.RequestException
                rest_framework.exceptions.ValidationError
        """
        response = self.core_client.post("/api/basket/{order_id}/items/return/".format(order_id=order_id), data=data)
        return response.json()["id"]

    def get_paginated_delta(self, start_date, limit_per_page=100):
        """
        :type start_date: datetime.datetime
        :type limit_per_page: int

        :rtype: collections.Iterable[list[inventorum.ebay.lib.core_api.models.CoreDeltaReturn]]
        :raises requests.exceptions.RequestError
                rest_framework.exceptions.ValidationError
        """
        params = {
            "channel": CoreChannel.EBAY,
            "start_date": self.core_client._encode_datetime(start_date)
        }

        pager = self.core_client.paginated_get("/api/returns/delta/", limit_per_page=limit_per_page, params=params)
        for page in pager.pages:
            serializer = CoreDeltaReturn.Serializer(data=page.data, many=True)
            yield serializer.build()
