# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.conf import settings

from inventorum.ebay.tests.testcases import UnitTestCase

from inventorum.ebay.apps.core_api.clients import CoreAPIClient


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
            "X-Api-Version": 9
        })

    def test_url_for(self):
        expected_host = settings.INV_CORE_API_HOST

        self.assertEqual(CoreAPIClient.url_for('/api/products'), "https://{host}/api/products"
                         .format(host=expected_host))

        self.assertEqual(CoreAPIClient.url_for('api/products'), "https://{host}/api/products"
                         .format(host=expected_host))

        self.assertEqual(CoreAPIClient.url_for('/'), "https://{host}/"
                         .format(host=expected_host))

        self.assertEqual(CoreAPIClient.url_for(''), "https://{host}/"
                         .format(host=expected_host))
