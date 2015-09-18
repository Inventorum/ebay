# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal as D
import logging
from datetime import datetime, timedelta
import unittest

from inventorum.ebay.tests.utils import PatchMixin

from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum.ebay.apps.products import EbayItemUpdateStatus
from inventorum.ebay.lib.core_api.tests import CoreApiTestHelpers
from inventorum.ebay.lib.core_api.tests.factories import CoreProductDeltaFactory
from inventorum.ebay.apps.products.core_products_sync import CoreProductsSync
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemVariationModel
from inventorum.ebay.apps.products.tasks import periodic_core_products_sync_task
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, PublishedEbayItemFactory
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context
from inventorum.ebay.tests import ApiTest, IntegrationTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase
from mock import PropertyMock
from rest_framework import status


log = logging.getLogger(__name__)


class IntegrationTestPeriodicCoreProductsSync(EbayAuthenticatedAPITestCase, CoreApiTestHelpers, ProductTestMixin):

    @celery_test_case()
    def test_integration(self):
        with IntegrationTest.use_cassette("core_products_sync_integration_test.yaml",
                                          filter_query_parameters=['start_date'], record_mode="never") as cassette:
            # create some core products to play with
            product_1_inv_id = self.create_core_api_product(name="Test product 1",
                                                            description="Awesome test products are awesome",
                                                            gross_price="1.99",
                                                            quantity=12)
            ebay_product_1 = self.get_valid_ebay_product_for_publishing(self.account, inv_id=product_1_inv_id)

            product_2_inv_id = self.create_core_api_product(name="Test product 2",
                                                            description="Awesome test products are awesome",
                                                            gross_price="3.45",
                                                            quantity=5)
            ebay_product_2 = self.get_valid_ebay_product_for_publishing(self.account, inv_id=product_2_inv_id)

            response = self.client.post("/products/%s/publish" % product_1_inv_id)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            response = self.client.post("/products/%s/publish" % product_2_inv_id)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            ebay_item_1 = ebay_product_1.published_item
            self.assertEqual(ebay_item_1.gross_price, D("1.99"))

            ebay_item_2 = ebay_product_2.published_item
            self.assertEqual(ebay_item_2.gross_price, D("3.45"))

            # ------------------------------------------------------------

            # product 1: update gross price
            self.update_core_api_product(product_1_inv_id, {
                "gross_price": "2.99"
            })

            periodic_core_products_sync_task.delay(context=get_anonymous_task_execution_context())

            # assert first update of product 1
            ebay_item_1 = ebay_product_1.items.first()
            self.assertEqual(ebay_item_1.updates.count(), 1)
            update = ebay_item_1.updates.first()

            self.assertEqual(update.gross_price, D("2.99"))
            self.assertEqual(update.quantity, None)
            self.assertEqual(update.status, EbayItemUpdateStatus.SUCCEEDED)

            # ebay item should have been updated as well
            ebay_item_1 = ebay_product_1.published_item
            self.assertEqual(ebay_item_1.gross_price, D("2.99"))

            # ------------------------------------------------------------

            # product 1: inventory adjustment
            self.adjust_core_inventory(product_1_inv_id, quantity=10, price="2.99")

            # run sync task
            periodic_core_products_sync_task.delay(context=get_anonymous_task_execution_context())

            # assert first update of product 1
            self.assertEqual(ebay_item_1.updates.count(), 2)
            update = ebay_item_1.updates.last()

            self.assertEqual(update.gross_price, None)
            self.assertEqual(update.quantity, 22)  # 12 initial + 10

            # ebay item should have been updated as well
            ebay_item_1 = ebay_product_1.published_item
            self.assertEqual(ebay_item_1.quantity, 22)

            # ------------------------------------------------------------

            self.delete_core_api_product(product_1_inv_id)
            self.delete_core_api_product(product_2_inv_id)

            # run sync task
            periodic_core_products_sync_task.delay(context=get_anonymous_task_execution_context())

            with self.assertRaises(EbayProductModel.DoesNotExist):
                EbayProductModel.objects.get(id=ebay_product_1.id)

            with self.assertRaises(EbayProductModel.DoesNotExist):
                EbayProductModel.objects.get(id=ebay_product_2.id)


class UnitTestCoreProductsSync(UnitTestCase):
    def setUp(self):
        super(UnitTestCoreProductsSync, self).setUp()

        # account with default user
        self.user = EbayUserFactory.create()
        self.account = self.user.account

        self.mock_dependencies()

    def mock_dependencies(self):
        core_api = "inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api"
        self.core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))

        schedule_ebay_item_update = "inventorum.ebay.apps.products.tasks.schedule_ebay_item_update"
        self.schedule_ebay_item_update_mock = self.patch(schedule_ebay_item_update)

        schedule_ebay_product_deletion = "inventorum.ebay.apps.products.tasks.schedule_ebay_product_deletion"
        self.schedule_ebay_product_deletion_mock = self.patch(schedule_ebay_product_deletion)

    def reset_mocks(self):
        self.core_api_mock.reset_mock()
        self.schedule_ebay_item_update_mock.reset_mock()
        self.schedule_ebay_product_deletion_mock.reset_mock()

    def expect_modified(self, *pages):
        mock = self.core_api_mock.get_paginated_product_delta_modified
        mock.reset_mock()
        mock.return_value = iter(pages)

    def expect_deleted(self, *pages):
        mock = self.core_api_mock.get_paginated_product_delta_deleted
        mock.reset_mock()
        mock.return_value = iter(pages)

    def test_basic_logic_with_empty_delta(self):
        assert self.account.last_core_products_sync is None

        subject = CoreProductsSync(account=self.account)

        self.expect_modified([])
        self.expect_deleted([])

        subject.run()

        self.core_api_mock.get_paginated_product_delta_modified.assert_called_once_with(
            start_date=self.account.time_added)
        self.core_api_mock.get_paginated_product_delta_deleted.assert_called_once_with(
            start_date=self.account.time_added)

        self.assertFalse(self.schedule_ebay_item_update_mock.called)
        self.assertFalse(self.schedule_ebay_product_deletion_mock.called)

        self.assertIsNotNone(self.account.last_core_products_sync)
        self.assertTrue(datetime.utcnow() - self.account.last_core_products_sync < timedelta(seconds=1))

        # next sync for the account should start from last_core_products_sync
        self.reset_mocks()

        # reload changes from database
        self.account = self.account.reload()

        last_core_products_sync = self.account.last_core_products_sync

        subject = CoreProductsSync(account=self.account)
        subject.run()

        self.core_api_mock.get_paginated_product_delta_modified.assert_called_once_with(
            start_date=last_core_products_sync)
        self.core_api_mock.get_paginated_product_delta_deleted.assert_called_once_with(
            start_date=last_core_products_sync)

    def test_unmapped_modified_and_deleted(self):
        # unmapped = products not connected to the ebay service
        subject = CoreProductsSync(account=self.account)

        self.expect_modified([
            CoreProductDeltaFactory.build(),
            CoreProductDeltaFactory.build()
        ])
        self.expect_deleted([1000, 1001, 1002])

        subject.run()

        self.assertFalse(self.schedule_ebay_item_update_mock.called)
        self.assertFalse(self.schedule_ebay_product_deletion_mock.called)

    @unittest.skip("only products that were published at least once are deleted, see core products sync for details")
    def test_unpublished_modified_and_deleted(self):
        subject = CoreProductsSync(account=self.account)

        # modified but not published, there should not be any updates
        product_a = EbayProductFactory.create(account=self.account, inv_id=1001)
        product_b = EbayProductFactory.create(account=self.account, inv_id=1002)

        self.expect_modified(
            [CoreProductDeltaFactory.build(id=1001)],  # page 1
            [CoreProductDeltaFactory.build(id=1002)]  # page 2
        )

        # deleted
        product_c = EbayProductFactory.create(account=self.account, inv_id=1003)
        product_d = EbayProductFactory.create(account=self.account, inv_id=1004)
        product_e = EbayProductFactory.create(account=self.account, inv_id=1005)

        self.expect_deleted([1003, 1004], [1005])

        subject.run()

        self.assertFalse(self.schedule_ebay_item_update_mock.called)

        self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 3)

        calls = self.schedule_ebay_product_deletion_mock.call_args_list
        self.assertEqual([args[0] for args, kwargs in calls], [product_c.id, product_d.id, product_e.id])

    def test_published_modified_and_deleted(self):
        subject = CoreProductsSync(account=self.account)

        # product a with updated quantity
        product_a = EbayProductFactory.create(account=self.account)
        item_a = PublishedEbayItemFactory.create(account=self.account,
                                                 product=product_a,
                                                 inv_product_id=1001,
                                                 gross_price=D("3.99"),
                                                 quantity=79)
        delta_a = CoreProductDeltaFactory(id=1001,
                                          gross_price=D("3.99"),
                                          quantity=78)

        # product b with updated gross price
        product_b = EbayProductFactory.create(account=self.account)
        item_b = PublishedEbayItemFactory.create(account=self.account,
                                                 product=product_b,
                                                 inv_product_id=1002,
                                                 gross_price=D("100.00"),
                                                 quantity=3)
        delta_b = CoreProductDeltaFactory(id=1002,
                                          gross_price=D("125.00"),
                                          quantity=3)

        # product c with updated gross price and quantity
        product_c = EbayProductFactory.create(account=self.account)
        item_c = PublishedEbayItemFactory.create(account=self.account,
                                                 product=product_c,
                                                 inv_product_id=1003,
                                                 gross_price=D("99.99"),
                                                 quantity=33)
        delta_c = CoreProductDeltaFactory(id=1003,
                                          gross_price=D("111.11"),
                                          quantity=22)

        # product d and e deleted
        product_d = EbayProductFactory.create(account=self.account)
        PublishedEbayItemFactory.create(account=self.account,
                                        product=product_d,
                                        inv_product_id=1004)
        product_e = EbayProductFactory.create(account=self.account)
        PublishedEbayItemFactory.create(account=self.account,
                                        product=product_e,
                                        inv_product_id=1005)

        assert all([p.is_published for p in [product_a, product_b, product_c, product_d, product_e]])

        self.expect_modified([delta_a], [delta_b], [delta_c])
        self.expect_deleted([1004, 1005])

        subject.run()

        # assert updates
        self.assertEqual(item_a.updates.count(), 1)
        item_a_update = item_a.updates.first()
        self.assertEqual(item_a_update.gross_price, None)  # not updated
        self.assertEqual(item_a_update.quantity, 78)

        self.assertEqual(item_b.updates.count(), 1)
        item_b_update = item_b.updates.first()
        self.assertEqual(item_b_update.gross_price, D("125.00"))
        self.assertEqual(item_b_update.quantity, None)  # not updated

        self.assertEqual(item_c.updates.count(), 1)
        item_c_update = item_c.updates.first()
        self.assertEqual(item_c_update.gross_price, D("111.11"))
        self.assertEqual(item_c_update.quantity, 22)

        self.assertEqual(self.schedule_ebay_item_update_mock.call_count, 3)
        calls = self.schedule_ebay_item_update_mock.call_args_list
        self.assertEqual([args[0] for args, kwargs in calls], [item_a_update.id, item_b_update.id, item_c_update.id])

        # assert deletions
        self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 2)

        calls = self.schedule_ebay_product_deletion_mock.call_args_list
        self.assertEqual([args[0] for args, kwargs in calls], [product_d.id, product_e.id])

    def test_published_modified_and_deleted_variations(self):
        subject = CoreProductsSync(account=self.account)

        # product a is our parent product
        product_a = EbayProductFactory.create(account=self.account, inv_id=1001)
        item_a = PublishedEbayItemFactory.create(account=self.account,
                                                 product=product_a,
                                                 inv_product_id=1001,
                                                 gross_price=None,
                                                 quantity=None)

        # variation a with just updated quantity
        variation_a = EbayItemVariationModel.create(
            item=item_a,
            quantity=5,
            gross_price=D("3.99"),
            tax_rate=D("7"),
            inv_product_id=1002
        )

        delta_variation_a = CoreProductDeltaFactory(id=variation_a.inv_product_id,
                                                    gross_price=D("3.99"),
                                                    quantity=78,
                                                    parent=item_a.inv_product_id)

        # variation b with updated gross price
        variation_b = EbayItemVariationModel.create(
            item=item_a,
            quantity=3,
            gross_price=D("100.0"),
            tax_rate=D("7"),
            inv_product_id=1003
        )
        delta_variation_b = CoreProductDeltaFactory(id=variation_b.inv_product_id,
                                                    gross_price=D("125.00"),
                                                    quantity=3,
                                                    parent=item_a.inv_product_id)

        # variation c with updated gross price and quantity
        variation_c = EbayItemVariationModel.create(
            item=item_a,
            quantity=33,
            gross_price=D("99.99"),
            tax_rate=D("7"),
            inv_product_id=1004
        )

        delta_variation_c = CoreProductDeltaFactory(id=variation_c.inv_product_id,
                                                    gross_price=D("111.11"),
                                                    quantity=22,
                                                    parent=item_a.inv_product_id)

        # variation d and e deleted
        variation_d = EbayItemVariationModel.create(
            item=item_a,
            quantity=33,
            gross_price=D("99.99"),
            tax_rate=D("7"),
            inv_product_id=1005
        )

        variation_e = EbayItemVariationModel.create(
            item=item_a,
            quantity=88,
            gross_price=D("88.88"),
            tax_rate=D("7"),
            inv_product_id=1006
        )

        self.assertTrue(product_a.is_published)
        self.assertEqual(product_a.published_item.variations.count(), 5)

        self.expect_modified([delta_variation_a], [delta_variation_b], [delta_variation_c])
        self.expect_deleted([variation_d.inv_product_id, variation_e.inv_product_id])

        subject.run()

        self.assertEqual(item_a.updates.count(), 1)
        self.assertEqual(item_a.updates.last().variations.count(), 5)
        self.assertEqual(variation_a.updates.count(), 1)

        variation_a_update = variation_a.updates.last()
        self.assertEqual(variation_a_update.gross_price, None)  # not updated
        self.assertEqual(variation_a_update.quantity, 78)

        self.assertEqual(variation_b.updates.count(), 1)
        variation_b_update = variation_b.updates.last()
        self.assertEqual(variation_b_update.gross_price, D("125.00"))
        self.assertEqual(variation_b_update.quantity, None)  # not updates

        self.assertEqual(variation_c.updates.count(), 1)
        variation_c_update = variation_c.updates.last()
        self.assertEqual(variation_c_update.gross_price, D("111.11"))
        self.assertEqual(variation_c_update.quantity, 22)

        self.assertEqual(variation_d.updates.count(), 1)
        variation_d_update = variation_d.updates.last()
        self.assertEqual(variation_d_update.gross_price, None)
        self.assertEqual(variation_d_update.quantity, 0)
        self.assertEqual(variation_d_update.is_deleted, True)

        self.assertEqual(variation_e.updates.count(), 1)
        variation_e_update = variation_e.updates.last()
        self.assertEqual(variation_e_update.gross_price, None)
        self.assertEqual(variation_e_update.quantity, 0)
        self.assertEqual(variation_e_update.is_deleted, True)

        self.assertEqual(self.schedule_ebay_item_update_mock.call_count, 1)
        # assert deletions
        self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 0)
