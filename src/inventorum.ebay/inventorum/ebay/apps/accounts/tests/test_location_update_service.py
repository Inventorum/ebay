# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from decimal import Decimal as D

from inventorum.ebay.apps.accounts.services import EbayLocationUpdateService, EbayLocationUpdateServiceException
from inventorum.ebay.apps.accounts.tests.factories import EbayLocationFactory
from inventorum.ebay.lib.core_api.tests import ApiTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestLocationUpdateService(EbayAuthenticatedAPITestCase):
    @ApiTest.use_cassette("test_update_ebay_location.yaml")
    def test_update(self):
        location = EbayLocationFactory.create(account=self.account)

        service = EbayLocationUpdateService(self.user)
        data = service.location_ebay_object.dict()
        self.assertDictEqual(data, {
            'Address1': location.address.street,
            'Address2': location.address.street1,
            'City': location.address.city,
            'Country': 'DE',
            'Hours': {'Day': [{'DayOfWeek': 1,
                               'Interval': [{'Close': '10:00:00',
                                             'Open': '08:00:00'}]},
                              {'DayOfWeek': 2,
                               'Interval': [{'Close': '14:00:00',
                                             'Open': '12:00:00'},
                                            {'Close': '20:00:00',
                                             'Open': '18:00:00'}]}]},
            'Latitude': location.latitude,
            'LocationID': 'invdev_346',
            'LocationType': 'STORE',
            'Longitude': location.longitude,
            'Name': location.name,
            'Phone': location.phone,
            'PickupInstructions': location.pickup_instruction,
            'PostalCode': location.address.postal_code,
            'Region': location.address.region,
            'URL': 'http://inventorum.com',
            'UTCOffset': '+02:00'}
        )

        # If this didnt raise any exception, everything is ok :-)
        service.update()

    @ApiTest.use_cassette("test_update_ebay_location_failing.yaml")
    def test_update_failing(self):
        location = EbayLocationFactory.create(account=self.account, longitude=D("9999.999"))

        service = EbayLocationUpdateService(self.user)
        with self.assertRaises(EbayLocationUpdateServiceException) as e:
            service.update()

        self.assertEqual(e.exception.message, u'AddInventoryLocation: Bad Request\n//Longitude: must be less than or equal to 180.00 Value: 9999.999')
