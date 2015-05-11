# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger

from inventorum.ebay.apps.categories.services import EbayCategoriesScraper, EbayFeaturesScraper, EbaySpecificsScraper
from django.conf import settings
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.util.celery import inventorum_task


log = get_task_logger(__name__)


def _get_ebay_token():
    """
    :rtype: EbayToken
    """
    return EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE)


@inventorum_task()
def ebay_categories_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    log.info('Syncing ebay categories...')
    try:
        service = EbayCategoriesScraper(ebay_token=_get_ebay_token())
        service.fetch_all()
    except EbayConnectionException as e:
        log.exception(e)


@inventorum_task()
def ebay_category_features_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    log.info('Syncing ebay category features...')
    try:
        features_service = EbayFeaturesScraper(ebay_token=_get_ebay_token())
        features_service.fetch_all()
    except EbayConnectionException as e:
        log.exception(e)


@inventorum_task()
def ebay_category_specifics_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    log.info('Syncing ebay category specifics...')
    try:
        specifics_service = EbaySpecificsScraper(ebay_token=_get_ebay_token())
        specifics_service.fetch_all()
    except EbayConnectionException as e:
        log.exception(e)


@inventorum_task()
def initialize_periodic_ebay_categories_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    categories_sync = ebay_categories_sync_task.si(context=self.context)
    features_sync = ebay_category_features_sync_task.si(context=self.context)
    specifics_sync = ebay_category_specifics_sync_task.si(context=self.context)

    (categories_sync | features_sync | specifics_sync)()
