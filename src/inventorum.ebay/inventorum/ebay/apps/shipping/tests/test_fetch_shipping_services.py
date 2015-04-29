# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.shipping.scripts import fetch_shipping_services
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestFetchCategories(UnitTestCase):

    def setUp(self):
        super(TestFetchCategories, self).setUp()
        self.scrape_mock = \
            self.patch('inventorum.ebay.apps.shipping.scripts.fetch_shipping_services.EbayShippingScraper.scrape')

    def test_script_invokes_correct_service_methods(self):
        fetch_shipping_services.run()
        self.assertTrue(self.scrape_mock.called)
