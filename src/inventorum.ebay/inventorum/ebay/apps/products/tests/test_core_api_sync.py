# # encoding: utf-8
# from __future__ import absolute_import, unicode_literals
# from decimal import Decimal as D
# import logging
#
# from inventorum.ebay.apps.categories.models import CategoryFeaturesModel, DurationModel
# from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
# from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient
#
# from datetime import datetime, timedelta
# from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory
# from inventorum.ebay.apps.products.scripts import core_api_sync
#
# from inventorum.ebay.apps.core_api.tests import CoreApiTestHelpers, ApiTest
# from inventorum.ebay.apps.core_api.tests.factories import CoreProductDeltaFactory
# from inventorum.ebay.apps.products.core_api_sync import CoreAPISyncService
# from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemUpdateModel
# from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, PublishedEbayItemFactory
# from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase
# from inventorum.ebay.tests.utils import PatchMixin
# from mock import PropertyMock
#
#
# log = logging.getLogger(__name__)
#
#
# class IntegrationTestCoreAPISync(EbayAuthenticatedAPITestCase, CoreApiTestHelpers, PatchMixin):
#
#     def setUp(self):
#         super(IntegrationTestCoreAPISync, self).setUp()
#         self.mock_dependencies()
#
#     def mock_dependencies(self):
#         # TODO: Remove mocks when ebay account is white listed
#         schedule_ebay_item_update = "inventorum.ebay.apps.products.tasks.schedule_ebay_item_update"
#         self.schedule_ebay_item_update_mock = self.patch(schedule_ebay_item_update)
#
#         schedule_ebay_product_deletion = "inventorum.ebay.apps.products.tasks.schedule_ebay_product_deletion"
#         self.schedule_ebay_product_deletion_mock = self.patch(schedule_ebay_product_deletion)
#
#     def reset_mocks(self):
#         self.schedule_ebay_item_update_mock.reset_mock()
#         self.schedule_ebay_product_deletion_mock.reset_mock()
#
#     @ApiTest.use_cassette("core_api_sync_integration_test.yaml", filter_query_parameters=['start_date'],
#                           record_mode="never")
#     def test_integration(self):
#         # create some core products to play with
#         self.product_1_inv_id = self.create_core_api_product(name="Test product 1",
#                                                              gross_price="1.99",
#                                                              quantity=12)
#         self.product_2_inv_id = self.create_core_api_product(name="Test product 2",
#                                                              gross_price="3.45",
#                                                              quantity=5)
#
#         # Map core products into ebay service
#         ebay_product_1 = EbayProductModel.objects.create(inv_id=self.product_1_inv_id, account=self.account)
#         # TODO jm: Actually publish to ebay when account is white listed
#         # response = self.client.post("/products/%s/publish" % self.product_1_inv_id)
#         # self.assertEqual(response.status_code, status.HTTP_200_OK)
#         PublishedEbayItemFactory(account=self.account,
#                                  product=ebay_product_1,
#                                  quantity=12,
#                                  gross_price="1.99")
#
#         ebay_product_2 = EbayProductModel.objects.create(inv_id=self.product_2_inv_id, account=self.account)
#         # TODO jm: Actually publish to ebay when account is white listed
#         # response = self.client.post("/products/%s/publish" % self.product_2_inv_id)
#         # self.assertEqual(response.status_code, status.HTTP_200_OK)
#         PublishedEbayItemFactory(account=self.account,
#                                  product=ebay_product_2,
#                                  gross_price="3.45",
#                                  quantity=5)
#
#         # Create and assign valid ebay category
#         # TODO jm: Extract to helper/factory
#         category = CategoryFactory.create(external_id="176973")
#         features = CategoryFeaturesModel.objects.create(
#             category=category
#         )
#         durations = ['Days_5', 'Days_30']
#         for d in durations:
#             duration = DurationModel.objects.create(
#                 value=d
#             )
#             features.durations.add(duration)
#
#         ebay_product_1.category = category
#         ebay_product_1.save()
#
#         ebay_product_2.category = category
#         ebay_product_2.save()
#
#         # ------------------------------------------------------------
#
#         # product 1: update gross price
#         self.update_core_api_product(self.product_1_inv_id, {
#             "gross_price": "2.99"
#         })
#
#         # run sync script
#         core_api_sync.run()
#
#         # assert first update of product 1
#         ebay_item_1 = ebay_product_1.items.first()
#         self.assertEqual(ebay_item_1.updates.count(), 1)
#         update = ebay_item_1.updates.first()
#
#         self.assertEqual(update.gross_price, D("2.99"))
#         self.assertEqual(update.quantity, None)
#
#         self.assertEqual(self.schedule_ebay_item_update_mock.call_count, 1)
#         self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 0)
#
#         self.reset_mocks()
#
#         # ------------------------------------------------------------
#
#         # Assume first update was successful
#         ebay_item_1.gross_price = D("2.99")
#         ebay_item_1.save()
#
#         # product 1: inventory adjustment
#         self.adjust_core_inventory(self.product_1_inv_id, quantity=10, price="2.99")
#
#         # run sync script
#         core_api_sync.run()
#
#         # assert first update of product 1
#         self.assertEqual(ebay_item_1.updates.count(), 2)
#         update = ebay_item_1.updates.last()
#
#         self.assertEqual(update.gross_price, None)
#         self.assertEqual(update.quantity, 22)  # 12 initial + 10
#
#         self.assertEqual(self.schedule_ebay_item_update_mock.call_count, 1)
#         self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 0)
#
#         self.reset_mocks()
#
#         # ------------------------------------------------------------
#
#         self.delete_core_api_product(self.product_1_inv_id)
#         self.delete_core_api_product(self.product_2_inv_id)
#
#         # run sync script
#         core_api_sync.run()
#
#         ebay_product_1 = ebay_product_1.reload()
#         self.assertEqual(ebay_product_1.deleted_in_core_api, True)
#
#         ebay_product_2 = ebay_product_2.reload()
#         self.assertEqual(ebay_product_2.deleted_in_core_api, True)
#
#         self.assertEqual(self.schedule_ebay_item_update_mock.call_count, 0)
#         self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 2)
#
#         self.reset_mocks()
#
#
# class UnitTestCoreAPISyncService(UnitTestCase):
#
#     def setUp(self):
#         super(UnitTestCoreAPISyncService, self).setUp()
#
#         self.account = EbayAccountFactory.create()
#         self.mock_dependencies()
#
#     def mock_dependencies(self):
#         core_api = "inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api"
#         self.core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))
#
#         schedule_ebay_item_update = "inventorum.ebay.apps.products.tasks.schedule_ebay_item_update"
#         self.schedule_ebay_item_update_mock = self.patch(schedule_ebay_item_update)
#
#         schedule_ebay_product_deletion = "inventorum.ebay.apps.products.tasks.schedule_ebay_product_deletion"
#         self.schedule_ebay_product_deletion_mock = self.patch(schedule_ebay_product_deletion)
#
#     def reset_mocks(self):
#         self.core_api_mock.reset_mock()
#         self.schedule_ebay_item_update_mock.reset_mock()
#         self.schedule_ebay_product_deletion_mock.reset_mock()
#
#     def expect_modified(self, *pages):
#         mock = self.core_api_mock.get_paginated_product_delta_modified
#         mock.reset_mock()
#         mock.return_value = iter(pages)
#
#     def expect_deleted(self, *pages):
#         mock = self.core_api_mock.get_paginated_product_delta_deleted
#         mock.reset_mock()
#         mock.return_value = iter(pages)
#
#     def test_basic_logic_with_empty_delta(self):
#         assert self.account.last_core_api_sync is None
#
#         subject = CoreAPISyncService(account=self.account)
#
#         self.expect_modified([])
#         self.expect_deleted([])
#
#         subject.run()
#
#         self.core_api_mock.get_paginated_product_delta_modified.assert_called_once_with(
#             start_date=self.account.time_added)
#         self.core_api_mock.get_paginated_product_delta_deleted.assert_called_once_with(
#             start_date=self.account.time_added)
#
#         self.assertFalse(self.schedule_ebay_item_update_mock.called)
#         self.assertFalse(self.schedule_ebay_product_deletion_mock.called)
#
#         self.assertIsNotNone(self.account.last_core_api_sync)
#         self.assertTrue(datetime.utcnow() - self.account.last_core_api_sync < timedelta(seconds=1))
#
#         # next sync for the account should start from last_core_api_sync
#         self.reset_mocks()
#
#         # reload changes from database
#         self.account = self.account.reload()
#
#         last_core_api_sync = self.account.last_core_api_sync
#
#         subject = CoreAPISyncService(account=self.account)
#         subject.run()
#
#         self.core_api_mock.get_paginated_product_delta_modified.assert_called_once_with(
#             start_date=last_core_api_sync)
#         self.core_api_mock.get_paginated_product_delta_deleted.assert_called_once_with(
#             start_date=last_core_api_sync)
#
#     def test_unmapped_modified_and_deleted(self):
#         # unmapped = products not connected to the ebay service
#         subject = CoreAPISyncService(account=self.account)
#
#         self.expect_modified([
#             CoreProductDeltaFactory.build(),
#             CoreProductDeltaFactory.build()
#         ])
#         self.expect_deleted([1000, 1001, 1002])
#
#         subject.run()
#
#         self.assertFalse(self.schedule_ebay_item_update_mock.called)
#         self.assertFalse(self.schedule_ebay_product_deletion_mock.called)
#
#     def test_unpublished_modified_and_deleted(self):
#         subject = CoreAPISyncService(account=self.account)
#
#         # modified but not published, there should not be any updates
#         product_a = EbayProductFactory.create(account=self.account, inv_id=1001)
#         product_b = EbayProductFactory.create(account=self.account, inv_id=1002)
#
#         self.expect_modified(
#             [CoreProductDeltaFactory.build(id=1001)],  # page 1
#             [CoreProductDeltaFactory.build(id=1002)]   # page 2
#         )
#
#         # deleted
#         product_c = EbayProductFactory.create(account=self.account, inv_id=1003)
#         product_d = EbayProductFactory.create(account=self.account, inv_id=1004)
#         product_e = EbayProductFactory.create(account=self.account, inv_id=1005)
#
#         self.expect_deleted([1003, 1004], [1005])
#
#         subject.run()
#
#         self.assertFalse(self.schedule_ebay_item_update_mock.called)
#
#         self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 3)
#
#         calls = self.schedule_ebay_product_deletion_mock.call_args_list
#         self.assertTrue(all([isinstance(args[0], EbayProductModel) for args, kwargs in calls]))
#         self.assertEqual([args[0].id for args, kwargs in calls], [product_c.id, product_d.id, product_e.id])
#
#     def test_published_modified_and_deleted(self):
#         subject = CoreAPISyncService(account=self.account)
#
#         # product a with updated quantity
#         product_a = EbayProductFactory.create(account=self.account, inv_id=1001)
#         item_a = PublishedEbayItemFactory.create(account=self.account,
#                                                  product=product_a,
#                                                  gross_price=D("3.99"),
#                                                  quantity=79)
#         delta_a = CoreProductDeltaFactory(id=product_a.inv_id,
#                                           gross_price=D("3.99"),
#                                           quantity=78)
#
#         # product b with updated gross price
#         product_b = EbayProductFactory.create(account=self.account, inv_id=1002)
#         item_b = PublishedEbayItemFactory.create(account=self.account,
#                                                  product=product_b,
#                                                  gross_price=D("100.00"),
#                                                  quantity=3)
#         delta_b = CoreProductDeltaFactory(id=1002,
#                                           gross_price=D("125.00"),
#                                           quantity=3)
#
#         # product c with updated gross price and quantity
#         product_c = EbayProductFactory.create(account=self.account, inv_id=1003)
#         item_c = PublishedEbayItemFactory.create(account=self.account,
#                                                  product=product_c,
#                                                  gross_price=D("99.99"),
#                                                  quantity=33)
#         delta_c = CoreProductDeltaFactory(id=1003,
#                                           gross_price=D("111.11"),
#                                           quantity=22)
#
#         # product d and e deleted
#         product_d = EbayProductFactory.create(account=self.account, inv_id=1004)
#         PublishedEbayItemFactory.create(account=self.account,
#                                         product=product_d)
#         product_e = EbayProductFactory.create(account=self.account, inv_id=1005)
#         PublishedEbayItemFactory.create(account=self.account,
#                                         product=product_e)
#
#         assert all([p.is_published for p in [product_a, product_b, product_c, product_d, product_e]])
#
#         self.expect_modified([delta_a], [delta_b], [delta_c])
#         self.expect_deleted([1004, 1005])
#
#         subject.run()
#
#         # assert updates
#         self.assertEqual(item_a.updates.count(), 1)
#         item_a_update = item_a.updates.first()
#         self.assertEqual(item_a_update.gross_price, None)  # not updated
#         self.assertEqual(item_a_update.quantity, 78)
#
#         self.assertEqual(item_b.updates.count(), 1)
#         item_b_update = item_b.updates.first()
#         self.assertEqual(item_b_update.gross_price, D("125.00"))
#         self.assertEqual(item_b_update.quantity, None)  # not updated
#
#         self.assertEqual(item_c.updates.count(), 1)
#         item_c_update = item_c.updates.first()
#         self.assertEqual(item_c_update.gross_price, D("111.11"))
#         self.assertEqual(item_c_update.quantity, 22)
#
#         self.assertEqual(self.schedule_ebay_item_update_mock.call_count, 3)
#         calls = self.schedule_ebay_item_update_mock.call_args_list
#         self.assertTrue(all([isinstance(args[0], EbayItemUpdateModel) for args, kwargs in calls]))
#         self.assertEqual([args[0].id for args, kwargs in calls], [item_a_update.id, item_b_update.id, item_c_update.id])
#
#         # assert deletions
#         self.assertEqual(self.schedule_ebay_product_deletion_mock.call_count, 2)
#
#         calls = self.schedule_ebay_product_deletion_mock.call_args_list
#         self.assertTrue(all([isinstance(args[0], EbayProductModel) for args, kwargs in calls]))
#         self.assertEqual([args[0].id for args, kwargs in calls], [product_d.id, product_e.id])
