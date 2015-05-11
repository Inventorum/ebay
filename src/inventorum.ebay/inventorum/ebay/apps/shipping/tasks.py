# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger

from django.conf import settings
from inventorum.ebay.apps.shipping.services import EbayShippingScraper
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.util.celery import inventorum_task


log = get_task_logger(__name__)


@inventorum_task()
def periodic_ebay_shipping_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    ebay_token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE)

    log.info('Fetching ebay shipping services...')
    subject = EbayShippingScraper(ebay_token)
    subject.scrape()
