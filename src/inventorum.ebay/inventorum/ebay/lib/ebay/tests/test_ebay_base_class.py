# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from ebaysdk.exception import ConnectionError

from inventorum.ebay.lib.ebay import Ebay, EbayConnectionException, EbayReturnedErrorsException
from inventorum.ebay.lib.ebay.tests import EbayClassTestCase
from django.conf import settings
from mock import Mock


class TestEbayBaseClass(EbayClassTestCase):

    def test_configuration(self):
        # It will call EbayTrading Connection class that we mocked
        ebay = Ebay(None)

        self.connection_mock.assert_called_once_with(
            appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
            certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
            debug=settings.DEBUG, timeout=20, config_file=None,
            compatibility=911, version=911, parallel=None)

        self.assertEqual(self.config.values['token'], None)
        self.assertEqual(self.config.values['siteid'], 77)

    def test_execute(self):
        ebay = Ebay(None)
        ebay.execute('Test', {})

        self.instance_mock.execute.assert_called_once_with(verb='Test', data={})

    def test_connection_handling(self):
        ebay = Ebay(None)

        error_response = Mock()
        error_response.dict.return_value = {'Errors': []}
        self.instance_mock.execute.side_effect = ConnectionError("test", error_response)
        self.assertRaises(EbayConnectionException, lambda: ebay.execute('Test', {}))

    def test_error_handling(self):
        ebay = Ebay(None)

        self.instance_mock.error.return_value = "Some errors"
        self.assertRaises(EbayReturnedErrorsException, lambda: ebay.execute('Test', {}))
