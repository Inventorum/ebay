# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal

from inventorum.ebay.tests import EbayTest, Countries
from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory

from inventorum.ebay.apps.shipping.models import ShippingServiceModel, ShippingServiceConfigurationModel
from inventorum.ebay.apps.shipping.services import EbayShippingScraper
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.apps.shipping.tests.factories import ShippingServiceFactory
from inventorum.ebay.lib.ebay.tests.factories import EbayShippingServiceFactory, EbayTokenFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase

log = logging.getLogger(__name__)


class IntegrationTestShippingScraper(EbayAuthenticatedAPITestCase):

    @EbayTest.use_cassette("ebay_get_shipping_details.yaml", match_on=["body"], record_mode="never")
    def test_shipping_scraper(self):
        subject = EbayShippingScraper(self.ebay_token)
        subject.scrape()

        DE_categories = ShippingServiceModel.objects.by_country(Countries.DE)
        self.assertEqual(DE_categories.count(), 20)

        AT_categories = ShippingServiceModel.objects.by_country(Countries.AT)
        self.assertEqual(AT_categories.count(), 14)

        # scrape again, because you know, scrapers gonna scrape
        db_service_ids_before = ShippingServiceModel.objects.values_list("id", flat=True)
        subject.scrape()

        # nothing should have been added or removed
        self.assertItemsEqual(ShippingServiceModel.objects.values_list("id", flat=True), db_service_ids_before)


class UnitTestShippingScraper(UnitTestCase, ShippingServiceTestMixin):

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
                                              shipping_time_max=3)
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

    def test_cascading_delete(self):
        account = EbayAccountFactory.create()
        product = EbayProductFactory.create()

        dhl_deleted = self.get_shipping_service_dhl()
        hermes_deleted = self.get_shipping_service_hermes()
        ups_preserved = self.get_shipping_service_ups()

        # should be deleted
        account.shipping_services.create(service=dhl_deleted, cost=Decimal("3.99"))
        product.shipping_services.create(service=hermes_deleted, cost=Decimal("4.90"))

        # should be preserved
        account.shipping_services.create(service=ups_preserved, cost=Decimal("0.00"))
        product.shipping_services.create(service=ups_preserved, cost=Decimal("5.40"))

        self.assertPrecondition(ShippingServiceModel.objects.count(), 3)
        self.assertPrecondition(account.shipping_services.count(), 2)
        self.assertPrecondition(product.shipping_services.count(), 2)

        self.expect_shipping_services_from_ebay([
            EbayShippingServiceFactory.create(id=ups_preserved.external_id)
        ])

        subject = EbayShippingScraper(ebay_token=self.ebay_token)
        subject.scrape()

        self.assertPostcondition(ShippingServiceModel.objects.by_country(Countries.DE).count(), 1)
        self.assertPostcondition(account.shipping_services.filter(service=ups_preserved).count(), 1)
        self.assertPostcondition(product.shipping_services.filter(service=ups_preserved).count(), 1)

    def test_skipping(self):
        valid_service = EbayShippingServiceFactory.create(id="ValidService")

        invalid_for_selling_flow = EbayShippingServiceFactory.create(id="InvalidService1",
                                                                     valid_for_selling_flow=False)
        with_dimensions_required = EbayShippingServiceFactory.create(id="InvalidService2",
                                                                     dimensions_required=True)
        international_service = EbayShippingServiceFactory.create(id="InvalidService3",
                                                                  international=True)

        self.expect_shipping_services_from_ebay([valid_service, invalid_for_selling_flow, with_dimensions_required,
                                                 international_service])

        subject = EbayShippingScraper(ebay_token=self.ebay_token)
        subject.scrape()

        imported_services = ShippingServiceModel.objects.by_country(Countries.DE)
        self.assertEqual(imported_services.count(), 1)

        self.assertTrue(imported_services.filter(external_id="ValidService").exists())
        self.assertFalse(imported_services.filter(external_id__in=["InvalidService1", "InvalidService2",
                                                                   "InvalidService3"]).exists())

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
