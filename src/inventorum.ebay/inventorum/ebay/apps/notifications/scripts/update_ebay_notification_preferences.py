# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.conf import settings
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.lib.ebay.data.authorization import EbayToken


log = logging.getLogger(__name__)


def run(*args):
    for country, site_id in settings.EBAY_SUPPORTED_SITES.iteritems():

        token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE,
                          site_id=site_id)

        log.info("Updating ebay notification settings for {}...".format(country))

        auth_api = EbayAuthentication(token=token)

        auth_api.execute("SetNotificationPreferences", {
            "ApplicationDeliveryPreferences": {
                "ApplicationURL": settings.EBAY_PLATFORM_NOTIFICATION_URL,
                "ApplicationEnable": "Enable",
                "DeviceType": "Platform"
            }
        })
