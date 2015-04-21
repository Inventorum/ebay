# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from celery.exceptions import MaxRetriesExceededError
from inventorum.ebay.apps.accounts.models import EbayUserModel
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.apps.products.services import PublishingService
from inventorum.ebay.lib.ebay import EbayConnectionException

from inventorum.util.celery import inventorum_task


log = logging.getLogger(__name__)


@inventorum_task(max_retries=10, default_retry_delay=10)
def _initialize_ebay_item_publish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    pass
    # try:
    #     raise Exception("Connection error")
    # except Exception:
    #     log.info("retrying initialize %s", ebay_item_id)
    #     self.retry()
    #     # will throw MaxRetriesExceededError and cancel chain


@inventorum_task()
def _ebay_item_publish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = PublishingService(ebay_item.product, user)

    try:
        service.publish(ebay_item)
    except EbayConnectionException as e:
        pass
        # try:
        #     self.retry()
        # except MaxRetriesExceededError:
        #     log.error()
        #     # mark as failed
        #     # will automatically move on to finalize_ebay_item_publish


@inventorum_task(max_retries=10, default_retry_delay=30)
def _finalize_ebay_item_publish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    pass
    # try:
    #     raise Exception("Finalize failure")
    # except Exception:
    #     self.retry()
    #     # will throw MaxRetriesExceededError and cancel chain


def schedule_ebay_item_publish(ebay_item_id, context):
    """
    :type ebay_item_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    init = _initialize_ebay_item_publish.si(ebay_item_id, context=context)
    publish = _ebay_item_publish.si(ebay_item_id, context=context)
    finalize = _finalize_ebay_item_publish.si(ebay_item_id, context=context)

    (init | publish | finalize)()
