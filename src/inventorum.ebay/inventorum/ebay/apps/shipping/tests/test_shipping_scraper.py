# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from inventorum.ebay.apps.core_api.tests import EbayTest
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.apps.shipping.services import EbayShippingScraper
from inventorum.ebay.tests import Countries
from inventorum.ebay.apps.shipping.tests.factories import ShippingServiceFactory
from inventorum.ebay.lib.ebay.tests.factories import EbayShippingServiceFactory, EbayTokenFactory

from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase

log = logging.getLogger(__name__)


class IntegrationTestShippingScraper(EbayAuthenticatedAPITestCase):

    @EbayTest.use_cassette("ebay_get_shipping_details.yaml", match_on=["body"], record_mode="new_episodes")
    def test_shipping_scraper(self):
        subject = EbayShippingScraper(self.ebay_token)
        subject.scrape()

        DE_categories = ShippingServiceModel.objects.by_country(Countries.DE)
        self.assertEqual(DE_categories.count(), 25)

        AT_categories = ShippingServiceModel.objects.by_country(Countries.AT)
        self.assertEqual(AT_categories.count(), 19)

        # scrape again, because you know, scrapers gonna scrape
        db_service_ids_before = ShippingServiceModel.objects.values_list("id", flat=True)
        subject.scrape()

        # nothing should have been added or removed
        self.assertItemsEqual(ShippingServiceModel.objects.values_list("id", flat=True), db_service_ids_before)


class UnitTestShippingScraper(UnitTestCase):

    def setUp(self):
        super(UnitTestShippingScraper, self).setUp()

        self.get_shipping_services_mock =\
            self.patch("inventorum.ebay.lib.ebay.details.EbayDetails.get_shipping_services")

        self.ebay_token = EbayTokenFactory.create()

    def expect_shipping_services_from_ebay(self, services):
        """
        :type services: list[inventorum.ebay.lib.ebay.details.EbayShippingService]
        """
        self.get_shipping_services_mock.return_value = services

    def test_scraping_and_delete(self):
        removed_db_service = ShippingServiceFactory.create(external_id="RemovedService_DB")

        self.expect_shipping_services_from_ebay([
            EbayShippingServiceFactory.create(id="CreatedService_Ebay",
                                              description="Awesome shipping service is awesome",
                                              shipping_time_min=1,
                                              shipping_time_max=3,
                                              international=True)
        ])

        subject = EbayShippingScraper(ebay_token=self.ebay_token)
        subject.scrape()

        db_services = ShippingServiceModel.objects.by_country(Countries.DE)
        self.assertEqual(db_services.count(), 1)

        with self.assertRaises(ShippingServiceModel.DoesNotExist):
            ShippingServiceModel.objects.get(pk=removed_db_service.pk)

        created_db_service = db_services.first()

        self.assertEqual(created_db_service.external_id, "CreatedService_Ebay")
        self.assertEqual(created_db_service.description, "Awesome shipping service is awesome")
        self.assertEqual(created_db_service.shipping_time_min, 1)
        self.assertEqual(created_db_service.shipping_time_max, 3)
        self.assertEqual(created_db_service.is_international, True)

    def test_skipping(self):
        valid_service = EbayShippingServiceFactory.create(id="ValidService")
        invalid_for_selling_flow = EbayShippingServiceFactory.create(id="InvalidService1",
                                                                     valid_for_selling_flow=False)
        with_dimensions_required = EbayShippingServiceFactory.create(id="InvalidService2",
                                                                     dimensions_required=True)

        self.expect_shipping_services_from_ebay([valid_service, invalid_for_selling_flow, with_dimensions_required])

        subject = EbayShippingScraper(ebay_token=self.ebay_token)
        subject.scrape()

        imported_services = ShippingServiceModel.objects.by_country(Countries.DE)
        self.assertEqual(imported_services.count(), 1)

        self.assertTrue(imported_services.filter(external_id="ValidService").exists())
        self.assertFalse(imported_services.filter(external_id__in=["InvalidService1", "InvalidService2"]).exists())

    def test_update(self):
        service = EbayShippingServiceFactory.create(id="ShippingService",
                                                    description="Original description",
                                                    shipping_time_min=1,
                                                    shipping_time_max=3)

        self.expect_shipping_services_from_ebay([service])

        subject = EbayShippingScraper(ebay_token=self.ebay_token)
        subject.scrape()

        self.assertTrue(ShippingServiceModel.objects.by_country(Countries.DE).count(), 1)

        service.description = "Updated description"
        service.shipping_time_min = 5
        service.shipping_time_max = 10
        self.expect_shipping_services_from_ebay([service])

        subject.scrape()

        self.assertTrue(ShippingServiceModel.objects.by_country(Countries.DE).count(), 1)

        db_repr = ShippingServiceModel.objects.by_country(Countries.DE).get(external_id=service.id)
        self.assertEqual(db_repr.description, "Updated description")
        self.assertEqual(db_repr.shipping_time_min, 5)
        self.assertEqual(db_repr.shipping_time_max, 10)
