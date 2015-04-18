# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient

from datetime import datetime, timedelta
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.core_api.tests import CoreApiTestHelpers
from inventorum.ebay.apps.products.core_api_sync import CoreAPISyncService
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase
from mock import PropertyMock


log = logging.getLogger(__name__)


class IntegrationTestCoreAPISync(EbayAuthenticatedAPITestCase, CoreApiTestHelpers):

    def xtest_integration(self):
        # Create some core products to play with
        product_1_inv_id = self.create_core_api_product(name="Test product 1", gross_price="1.99", quantity=12)
        product_2_inv_id = self.create_core_api_product(name="Test product 2", gross_price="3.45", quantity=5)
        product_3_inv_id = self.create_core_api_product(name="Test product 3", gross_price="9.99", quantity=100)

        # Map core products into ebay service
        ebay_product_1 = EbayProductModel.objects.create(inv_id=product_1_inv_id, account=self.account)
        ebay_product_2 = EbayProductModel.objects.create(inv_id=product_2_inv_id, account=self.account)
        ebay_product_3 = EbayProductModel.objects.create(inv_id=product_3_inv_id, account=self.account)

        # Publish some core products to ebay
        # response = self.client.post("/products/%s/publish" % product_1_inv_id)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # response = self.client.post("/products/%s/publish" % product_2_inv_id)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make some changes
        self.update_core_api_product(product_1_inv_id, {})

        self.delete_core_api_product(product_2_inv_id)

        self.update_core_api_product(product_3_inv_id, {})

        self.delete_core_api_product(product_1_inv_id)
        self.delete_core_api_product(product_3_inv_id)


class UnitTestCoreAPISyncService(UnitTestCase):

    def setUp(self):
        self.account = EbayAccountFactory.create()
        self.mock_dependencies()

    def mock_dependencies(self):
        core_api = "inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api"
        self.core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))

        schedule_ebay_item_unpublish = "inventorum.ebay.apps.products.tasks.schedule_ebay_item_unpublish"
        self.schedule_ebay_item_unpublish_mock = self.patch(schedule_ebay_item_unpublish)

        schedule_ebay_item_update = "inventorum.ebay.apps.products.tasks.schedule_ebay_item_update"
        self.schedule_ebay_item_update_mock = self.patch(schedule_ebay_item_update)

        schedule_ebay_product_delete = "inventorum.ebay.apps.products.tasks.schedule_ebay_product_delete"
        self.schedule_ebay_product_delete_mock = self.patch(schedule_ebay_product_delete)

    def reset_mocks(self):
        self.core_api_mock.reset_mock()
        self.schedule_ebay_item_unpublish_mock.reset_mock()
        self.schedule_ebay_item_update_mock.reset_mock()
        self.schedule_ebay_product_delete_mock.reset_mock()

    def expect_modified(self, pages):
        if pages is []:
            pages.append([])

        mock = self.core_api_mock.get_paginated_product_delta_modified
        mock.reset_mock()
        mock.return_value = iter(pages)

    def expect_deleted(self, pages):
        if pages is []:
            pages.append([])

        mock = self.core_api_mock.get_paginated_product_delta_deleted
        mock.reset_mock()
        mock.return_value = iter(pages)

    def test_basic_logic_with_empty_delta(self):
        assert self.account.last_core_api_sync is None

        subject = CoreAPISyncService(account=self.account)

        self.expect_modified([])
        self.expect_deleted([])

        subject.run()

        self.core_api_mock.get_paginated_product_delta_modified.assert_called_once_with(
            start_date=self.account.time_added)
        self.core_api_mock.get_paginated_product_delta_deleted.assert_called_once_with(
            start_date=self.account.time_added)

        self.assertFalse(self.schedule_ebay_item_unpublish_mock.called)
        self.assertFalse(self.schedule_ebay_item_update_mock.called)
        self.assertFalse(self.schedule_ebay_product_delete_mock.called)

        self.assertIsNotNone(self.account.last_core_api_sync)
        self.assertTrue(datetime.utcnow() - self.account.last_core_api_sync < timedelta(seconds=1))

        # next sync for the account should start from last_core_api_sync
        self.reset_mocks()

        # reload changes from database
        self.account = self.account.reload()

        last_core_api_sync = self.account.last_core_api_sync

        subject = CoreAPISyncService(account=self.account)
        subject.run()

        self.core_api_mock.get_paginated_product_delta_modified.assert_called_once_with(
            start_date=last_core_api_sync)
        self.core_api_mock.get_paginated_product_delta_deleted.assert_called_once_with(
            start_date=last_core_api_sync)
