# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime
from django.utils.functional import cached_property
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.products import tasks, EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemUpdateModel, \
    EbayItemVariationModel, EbayItemVariationUpdateModel
from inventorum.util.celery import TaskExecutionContext
from inventorum.util.django.middlewares import fallback_uuid


log = logging.getLogger(__name__)


class CoreOrdersSync(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def get_task_execution_context(self):
        """
        :rtype: inventorum.util.celery.TaskExecutionContext
        """
        return TaskExecutionContext(user_id=self.account.default_user.id,
                                    account_id=self.account.id,
                                    request_id=None)

    def run(self):
        current_sync_start = datetime.utcnow()
        # if there was no sync yet, the ebay account creation is taken as starting point
        last_sync_start = self.account.last_core_orders_sync or self.account.time_added

        modified_ebay_orders = self._get_modified_ebay_orders(modified_since=last_sync_start)
        for order, core_order in modified_ebay_orders:
            log.info(order.ebay_id)

        self.account.last_core_orders_sync = current_sync_start
        self.account.save()

    def _get_modified_ebay_orders(self, modified_since):
        """
        :type modified_since:
        :rtype: collections.Iterable[(inventorum.ebay.apps.orders.models.OrderModel, inventorum.ebay.apps.core_api.models.CoreOrder)]
        """
        pages = self.account.core_api.get_paginated_orders_delta(start_date=modified_since)
        for page in pages:
            log.info(page)
            for core_order in page:
                ebay_order = OrderModel.objects.by_inv_id(core_order.inv_id).get()
                yield ebay_order, core_order
