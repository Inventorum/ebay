# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import requests

from django.conf import settings

log = logging.getLogger(__name__)


class CoreAPIClient(object):

    @property
    def default_headers(self):
        """
        :return: The default headers that are sent with every request unless explicitly overwritten
        :rtype: dict
        """
        return {
            "User-Agent": "inv-ebay/{version}".format(version=settings.VERSION),
            "Content-Type": "application/json",
            "Accept": "application/json"
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

        return "https://{host}{path}".format(host=settings.INV_CORE_API_HOST, path=path)

    def get(self, path, params=None, headers=None):
        """
        Performs a get request to the given core api path with the given params/headers

        :param path: The core api request path
        :param params: Optional URL params
        :param headers: Optional HTTP headers
        :return: The response as JSON

        :type path: str | unicode
        :type params: dict
        :type headers: dict

        :rtype: valid JSON type, see https://docs.python.org/2/library/json.html#json.loads
        """
        if params is None:
            params = {}

        if headers is None:
            headers = {}

        headers_with_defaults = self.default_headers
        headers_with_defaults.update(headers)

        response = requests.get(self.url_for(path), params=params, headers=headers_with_defaults)
        return response.json()


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

    def get_product_details(self, inv_product_id):
        raise NotImplemented
