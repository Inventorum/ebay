# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger

from inventorum.ebay.apps.categories.services import EbayCategoriesScraper, EbayFeaturesScraper, EbaySpecificsScraper
from django.conf import settings

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
    service = EbayCategoriesScraper(ebay_token=_get_ebay_token())
    service.fetch_all()


@inventorum_task()
def ebay_category_features_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    log.info('Syncing ebay category features...')
    features_service = EbayFeaturesScraper(ebay_token=_get_ebay_token())
    features_service.fetch_all()

@inventorum_task()
def ebay_category_specifics_batch_task(self, categories_ids, country_code):

    log.info('Syncing ebay category specifics (country: %s) for ids: %s', country_code, categories_ids)
    specifics_service = EbaySpecificsScraper(ebay_token=_get_ebay_token())
    limited_qs = specifics_service.get_queryset_with_country(country_code).filter(id__in=categories_ids)
    specifics_service.fetch(limited_qs, country_code)

@inventorum_task()
def ebay_category_specifics_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    log.info('Syncing ebay category specifics...')
    specifics_service = EbaySpecificsScraper(ebay_token=_get_ebay_token())
    for country_code in settings.EBAY_SUPPORTED_SITES.keys():
        batches = specifics_service.batch_queryset(specifics_service.get_queryset_with_country(country_code))
        for limited_qs in batches:
            ids = list(limited_qs.values_list('id', flat=True))
            ebay_category_specifics_batch_task.delay(ids, country_code, context=self.context)


@inventorum_task()
def initialize_periodic_ebay_categories_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    categories_sync = ebay_categories_sync_task.si(context=self.context)
    features_sync = ebay_category_features_sync_task.si(context=self.context)
    specifics_sync = ebay_category_specifics_sync_task.si(context=self.context)

    (categories_sync | features_sync | specifics_sync)()
