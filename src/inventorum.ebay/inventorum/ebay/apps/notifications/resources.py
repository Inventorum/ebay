# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from rest_framework.serializers import Serializer

import six

from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from inventorum.ebay.apps.notifications.models import EbayNotificationModel
from inventorum.ebay.apps.notifications.services import EbayPlatformNotificationService
from inventorum.ebay.lib.rest.resources import PublicAPIResource
from inventorum.ebay.lib.ebay.notifications import EbayNotification


log = logging.getLogger(__name__)


class EbayPlatformNotificationsResource(PublicAPIResource):
    """
    Resource to handle public ebay platfrom notifications
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = Serializer
    
    @transaction.atomic
    def post(self, request):
        """
        Public callback action for ebay platform notifications
        http://developer.ebay.com/Devzone/guides/ebayfeatures/Notifications/Notifications.html

        :type request: rest_framework.request.Request

        ---
        omit_serializer: true
        """
        cleaned_request_headers = {unicode(key): unicode(value) for key, value in request.META.iteritems()
                                   if isinstance(value, six.string_types)}
        log.info("Received ebay platform notification with request headers {} and request body: {}"
                 .format(cleaned_request_headers, unicode(request.body, "utf-8")))

        try:
            notification = EbayNotification(body=request.body, headers=request.META)
            notification.validate_signature(settings.EBAY_DEVID, settings.EBAY_APPID, settings.EBAY_CERTID)
        except EbayNotification.ParseError as e:
            log.error("Could not parse ebay notification: %s", e.message)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except EbayNotification.SignatureValidationError as e:
            log.error("Invalid signature of ebay notification: %s", e.message)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        model = EbayNotificationModel.create_from_ebay_notification(notification)
        EbayPlatformNotificationService.handle(model)

        # always return 200, otherwise ebay will consider the response as failure and might block us
        return Response(status=status.HTTP_200_OK)
