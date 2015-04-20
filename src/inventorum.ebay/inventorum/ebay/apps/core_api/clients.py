# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.models import CoreProductDeserializer, CoreAccountDeserializer, CoreInfoDeserializer
import requests

from django.conf import settings

log = logging.getLogger(__name__)


class CoreAPIClient(object):
    API_VERSION = 9

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
        if params is None:
            params = {}

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

        :param product_id:
        :return:

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

    def send_state(self, inv_product_id, state, details):
        """
        Send state about publishing product to Inventorum api. Returns nothing, in case of failure raises
        :param inv_product_id: Product id of inventorum database
        :param state: State of publishing (check PublishStates)
        :param details: Additional details (optional)
        """
        data = {
            'channel': 'ebay',
            'state': state,
            'details': details or {'success': True}
        }
        self.post('/api/products/{}/state/'.format(inv_product_id), data=data)