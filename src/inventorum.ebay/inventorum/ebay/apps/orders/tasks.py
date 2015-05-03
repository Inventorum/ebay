# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.models import EbayUserModel, EbayAccountModel
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.orders.services import CoreOrderService

from inventorum.util.celery import inventorum_task
from requests.exceptions import RequestException


log = logging.getLogger(__name__)


@inventorum_task(max_retries=5, default_retry_delay=30)
def core_order_creation_task(self, order_id):
    """
    :type order_id: int
    """
    account = EbayAccountModel.objects.get(id=self.context.account_id)
    order = OrderModel.objects.get(id=order_id)

    service = CoreOrderService(account)

    try:
        service.create_in_core_api(order)
    except RequestException as e:
        self.retry()


def schedule_core_order_creation(order_id, context):
    """
    :type order_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    core_order_creation_task.delay(order_id=order_id, context=context)
