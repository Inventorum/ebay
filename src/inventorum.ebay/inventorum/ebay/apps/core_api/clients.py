# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import json
import logging
from inventorum.ebay.apps.core_api.models import CoreProductDeserializer, CoreInfoDeserializer, \
    CoreProductDeltaDeserializer
from inventorum.ebay.apps.core_api.pager import Pager
import requests

from django.conf import settings
from inventorum.ebay.apps.inventory.serializers import QuantityCoreApiResponseDeserializer

log = logging.getLogger(__name__)


class CoreAPIClientException(Exception):
    pass


class CoreAPIClient(object):
    API_VERSION = 9
    EBAY_CHANNEL = "ebay"

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
            "X-Api-Version": self.API_VERSION
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

        :raises requests.exceptions.HTTPError
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

        :raises requests.exceptions.HTTPError
        """
        if params is None:
            params = {}

        if custom_headers is None:
            custom_headers = {}

        if data is None:
            data = {}

        headers = self.default_headers
        headers.update(custom_headers)

        response = requests.post(self.url_for(path), json=data, params=params, headers=headers)

        if not response.ok:
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

        :raises requests.exceptions.HTTPError
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

        :raises requests.exceptions.HTTPError
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

        :raises requests.exceptions.HTTPError, inventorum.ebay.apps.core_api.pager.PagerException
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
        :raises requests.exceptions.HTTPError
                rest_framework.exceptions.ValidationError
        """
        response = self.get("/api/products/{product_id}".format(product_id=product_id))
        json = response.json()
        log.debug('Got json from /api/products/%s/: %s', product_id, json)
        serializer = CoreProductDeserializer(data=json)
        return serializer.build()

    def get_account_info(self):
        """
        :rtype: inventorum.ebay.apps.core_api.models.CoreInfo
        :raises requests.exceptions.HTTPError
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
        :raises requests.exceptions.HTTPError
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
        :raises requests.exceptions.HTTPError
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
        :raises requests.exceptions.HTTPError
                rest_framework.exceptions.ValidationError
        """
        params = {
            "start_date": self._encode_datetime(start_date)
        }
        pager = self.paginated_get("/api/products/delta/deleted/", limit_per_page=limit_per_page, params=params)
        for page in pager.pages:
            yield page.data

    def post_product_publishing_state(self, inv_product_id, state, details):
        """
        Send state about publishing product to Inventorum api. Returns nothing, in case of failure raises
        :param inv_product_id: Product id of inventorum database
        :param state: State of publishing (check PublishStates)
        :param details: Additional details (optional)
        """
        data = {
            'channel': 'ebay',
            'state': state,
            'details': details
        }
        return self.post('/api/products/{}/state/'.format(inv_product_id), data=data)

    def create_order(self, data):
        """

        :param data:
        :return:
        """
        return self.post('/api/orders?channel={}'.format(self.EBAY_CHANNEL), data=data)
