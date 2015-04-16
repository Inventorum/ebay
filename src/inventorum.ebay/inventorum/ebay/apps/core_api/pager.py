# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging
from math import ceil
from django.utils.functional import cached_property

log = logging.getLogger(__name__)


class PagerException(Exception):
    pass


class Page(object):
    """ Simple value object representing a page """
    def __init__(self, pager, number, response, data):
        """
        :type pager: Pager
        :type number: int
        :type response: requests.models.Response
        :type data: dict
        """
        self.pager = pager

        self.number = number
        self.response = response
        self.data = data


class Pager(object):

    def __init__(self, client, path, limit_per_page, params=None, custom_headers=None):
        """
        :type client: inventorum.ebay.apps.core_api.clients.CoreAPIClient
        :type path: str | unicode
        :type limit_per_page: int
        :type params: dict
        :type custom_headers: dict

        :raises requests.exceptions.HTTPError, PagerException
        """
        if params is None:
            params = {}

        self.client = client
        self.path = path
        self.limit_per_page = limit_per_page
        self.params = params
        self.custom_headers = custom_headers

        self._init_with_initial_request()

    @property
    def total_items(self):
        """
        :return: The total number of items across all pages
        :rtype: int
        """
        return self._total_items

    @property
    def total_pages(self):
        """
        :return: The total number of pages
        :rtype: int
        """
        return self._total_pages

    @cached_property
    def pages(self):
        """
        :return: An iterator over all pages
        :rtype: collections.Iterable[Page]

        :raises requests.exceptions.HTTPError, PagerException
        """
        yield Page(pager=self, number=1, response=self._initial_response, data=self._initial_json_body["data"])

        for i in range(2, self.total_pages + 1):
            response = self._request_page(i)
            json_body = self._parse_and_validate_json(response)
            yield Page(pager=self, number=i, response=response, data=json_body["data"])

    def _init_with_initial_request(self):
        """
        Initializes the pager by requesting the first page to determine the total number of items and pages
        """
        initial_response = self._request_page(1)
        initial_json_body = self._parse_and_validate_json(initial_response)

        try:
            self._total_items = int(initial_json_body["total"])
        except (ValueError, TypeError):
            raise PagerException("Malformed response body: Invalid `total` received in '{}'".format(initial_json_body))

        self._total_pages = max(1, int(ceil(Decimal(self.total_items) / self.limit_per_page)))

        # cached for yielding the first page
        self._initial_response = initial_response
        self._initial_json_body = initial_json_body

    def _parse_and_validate_json(self, response):
        """
        :type response: requests.models.Response
        :rtype: dict

        :raises PagerException
        """
        try:
            json_body = response.json()
        except (ValueError, TypeError):
            raise PagerException("Malformed response body: {}".format(response.content))

        if "total" not in json_body:
            raise PagerException("Malformed response body: No `total` received in '{}'".format(json_body))

        if "data" not in json_body:
            raise PagerException("Malformed response body: No `data` received in '{}'".format(json_body))

        return json_body

    def _request_page(self, page):
        """
        Requests the given page via the core api client

        :type page: int
        :rtype: requests.models.Response

        :raises requests.exceptions.HTTPError
        """
        params = self.params.copy()
        params["page"] = page
        params["limit"] = self.limit_per_page

        return self.client.get(self.path, params, self.custom_headers)
