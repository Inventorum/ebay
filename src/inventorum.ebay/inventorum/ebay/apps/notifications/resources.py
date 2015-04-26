# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings
from inventorum.ebay.lib.rest.resources import PublicAPIResource
from inventorum.ebay.lib.ebay.notifications import EbayNotification
from rest_framework import status

from rest_framework.response import Response


log = logging.getLogger(__name__)


class EbayPlatformNotificationsResource(PublicAPIResource):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        """
        Public callback action for ebay platform notifications
        http://developer.ebay.com/Devzone/guides/ebayfeatures/Notifications/Notifications.html

        :type request: rest_framework.request.Request
        """
        try:
            notification = EbayNotification(body=request.body, headers=request.META)
            notification.validate_signature(settings.EBAY_DEVID, settings.EBAY_APPID, settings.EBAY_CERTID)
        except EbayNotification.ParseError as e:
            log.error("Could not parse ebay notification: %s", e.message)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except EbayNotification.SignatureValidationError as e:
            log.error("Invalid signature of ebay notification: %s", e.message)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # always return 200, otherwise ebay will consider the response as failure and might block us
        return Response(status=status.HTTP_200_OK)
