# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.tests.testcases import UnitTestCase
from mock import patch

from inventorum.ebay.apps.categories.scripts import fetch_categories


class TestFetchCategories(UnitTestCase):
    @patch('inventorum.ebay.apps.categories.scripts.fetch_categories.EbayCategoriesScraper')
    @patch('inventorum.ebay.apps.categories.scripts.fetch_categories.EbayFeaturesScraper')
    @patch('inventorum.ebay.apps.categories.scripts.fetch_categories.EbaySpecificsScraper')
    def test_it_calls_corect_service(self, specifics_mock, features_mock, scrapper_mock):
        specifics_instance_mock = specifics_mock.return_value
        features_instance_mock = features_mock.return_value
        scrapper_instance_mock = scrapper_mock.return_value

        fetch_categories.run()
        specifics_instance_mock.fetch_all.assert_called_once_with()