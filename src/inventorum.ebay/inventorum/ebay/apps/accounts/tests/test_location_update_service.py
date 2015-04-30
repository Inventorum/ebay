# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from decimal import Decimal as D

from inventorum.ebay.apps.accounts.services import EbayLocationUpdateService
from inventorum.ebay.apps.accounts.tests.factories import EbayLocationFactory
from inventorum.ebay.apps.core_api.tests import ApiTest
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
            'Region': '',
            'URL': 'http://inventorum.com',
            'UTCOffset': '+02:00'}
        )
        service.update()