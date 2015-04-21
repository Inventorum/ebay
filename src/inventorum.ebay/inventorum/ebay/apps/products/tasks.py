# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from celery.app import shared_task
from celery.exceptions import MaxRetriesExceededError

from inventorum.util.celery import inventorum_task


log = logging.getLogger(__name__)


@inventorum_task()
def foo(self):
    raise Exception("celery works!")


@inventorum_task(max_retries=10, default_retry_delay=10)
def _initialize_ebay_item_publish(self, ebay_item_id):
    log.info("initialize")

    try:
        raise Exception("Connection error")
    except Exception:
        try:
            self.retry()
        except MaxRetriesExceededError:
            log.error("Failed")


@inventorum_task(max_retries=3, default_retry_delay=60)
def _ebay_item_publish(self, ebay_item_id):
    log.info("publish")


@inventorum_task(max_retries=10, default_retry_delay=30)
def _finalize_ebay_item_publish(self, ebay_item_id):
    log.info("finalize")


def schedule_ebay_item_publish(ebay_item_id, context):
    """
    :type ebay_item_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    init = _initialize_ebay_item_publish.si(ebay_item_id, context=context)
    publish = _ebay_item_publish.si(ebay_item_id, context=context)
    finalize = _finalize_ebay_item_publish.si(ebay_item_id, context=context)

    (init | publish | finalize)()
