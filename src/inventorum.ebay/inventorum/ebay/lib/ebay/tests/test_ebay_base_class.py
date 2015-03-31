from ebaysdk.trading import Connection
from inventorum.ebay.lib.ebay import Ebay
from inventorum.ebay.tests.testcases import APITestCase
from mock import patch
from django.conf import settings


class ConfigMocked(object):
    values = {}

    def set(self, key, value):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key, None)


class TestEbayBaseClass(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(TestEbayBaseClass, cls).setUpClass()
        cls.connection_original = Connection
        cls.patcher = patch('inventorum.ebay.lib.ebay.Connection', spec=True)
        cls.connection_mock = cls.patcher.start()
        cls.instance_mock = cls.connection_mock.return_value

        cls.config = ConfigMocked()
        cls.instance_mock.config = cls.config

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
        super(TestEbayBaseClass, cls).tearDownClass()

    def test_configuration(self):
        # It will call EbayTrading Connection class that we mocked
        ebay = Ebay(None)

        self.connection_mock.assert_called_once_with(
            appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
            certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
            debug=settings.DEBUG, timeout=20,
            compatibility=911, version=911)

        self.assertEqual(self.config.values['token'], None)
        self.assertEqual(self.config.values['siteid'], 77)

