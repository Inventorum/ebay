# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.categories.services import EbayCategoriesScraper, EbayFeaturesScraper
from django.conf import settings
from inventorum.ebay.lib.ebay.data import EbayToken

log = logging.getLogger(__name__)


def run(*args):
    token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE)

    log.debug('Fetching ebay categories...')
    service = EbayCategoriesScraper(ebay_token=token)
    service.fetch_all()

    log.debug('Fetching ebay features...')
    features_service = EbayFeaturesScraper(token)
    features_service.fetch_all()