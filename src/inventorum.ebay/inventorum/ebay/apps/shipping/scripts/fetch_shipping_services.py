# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings
from inventorum.ebay.apps.shipping.services import EbayShippingScraper
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.authorization import EbayToken

log = logging.getLogger(__name__)


def run(*args):
    ebay_token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE)

    log.info('Fetching ebay shipping services...')

    try:
        subject = EbayShippingScraper(ebay_token)
        subject.scrape()
    except EbayConnectionException:
        log.exception("Got exception from ebay when getting shipping services")
