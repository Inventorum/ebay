# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.categories import EbayCategories
from inventorum.ebay.lib.ebay.tests import EbayClassTestCase
from django.conf import settings


class EbayCategoriesTest(EbayClassTestCase):
    def test_init(self):
        ebay = EbayCategories(None)


        self.connection_mock.assert_any_call(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                                             certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                                             debug=settings.DEBUG, timeout=20, config_file=None,
                                             compatibility=911, version=911, parallel=None)
        # Make sure parallel object was created
        self.connection_mock.assert_any_call(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                                             certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                                             debug=settings.DEBUG, timeout=20, config_file=None,
                                             compatibility=911, version=911, parallel=self.parallel_mock)

        ebay.get_attributes_for_categories([1, 2, 3])
        self.parallel_mock.wait.assert_called_with(ebay.timeout)