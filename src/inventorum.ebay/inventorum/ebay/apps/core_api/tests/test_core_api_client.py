# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.conf import settings
from inventorum.ebay.apps.core_api import PaginatedFakeCoreAPIResponse
from inventorum.ebay.apps.core_api.pager import Pager

from inventorum.ebay.tests.testcases import UnitTestCase

from inventorum.ebay.apps.core_api.clients import CoreAPIClient
from mock import patch


log = logging.getLogger(__name__)


class TestCoreAPIClient(UnitTestCase):

    def setUp(self):
        super(TestCoreAPIClient, self).setUp()

        self.subject = CoreAPIClient()

    def test_default_headers(self):
        expected_version = settings.VERSION

        self.assertEqual(self.subject.default_headers, {
            "User-Agent": "inv-ebay/{version}".format(version=expected_version),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Version": 10
        })

    def test_url_for(self):
        expected_host = settings.INV_CORE_API_HOST

        self.assertEqual(CoreAPIClient.url_for('/api/products'), "http://{host}/api/products"
                         .format(host=expected_host))

        self.assertEqual(CoreAPIClient.url_for('api/products'), "http://{host}/api/products"
                         .format(host=expected_host))

        self.assertEqual(CoreAPIClient.url_for('/'), "http://{host}/"
                         .format(host=expected_host))

        self.assertEqual(CoreAPIClient.url_for(''), "http://{host}/"
                         .format(host=expected_host))

    @patch.object(CoreAPIClient, 'get')
    def test_paginated_get_initializes_and_returns_correct_pager(self, mocked_get):
        # provide a plain fake response for the initial pager request
        mocked_get.return_value = PaginatedFakeCoreAPIResponse()

        pager = self.subject.paginated_get(path="/api/products",
                                           limit_per_page=10,
                                           params={"foo": "bar"},
                                           custom_headers={"X-Inv-Foo": "bar"})

        self.assertTrue(type(pager), Pager)
        self.assertEqual(pager.path, "/api/products")
        self.assertEqual(pager.limit_per_page, 10)
        self.assertEqual(pager.params, {"foo": "bar"})
        self.assertEqual(pager.custom_headers, {"X-Inv-Foo": "bar"})
