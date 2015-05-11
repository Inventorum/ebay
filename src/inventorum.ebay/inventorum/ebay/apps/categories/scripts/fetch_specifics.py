# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.categories.services import EbaySpecificsScraper
from django.conf import settings
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.authorization import EbayToken

log = logging.getLogger(__name__)


def run(*args):
    token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE)
    log.info('Fetching ebay specifics per category...')
    try:
        specifics_service = EbaySpecificsScraper(ebay_token=token)
        specifics_service.fetch_all()
    except EbayConnectionException as e:
        log.exception("Got exception from ebay when getting specifics")
