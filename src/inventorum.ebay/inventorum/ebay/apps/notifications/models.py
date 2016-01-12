# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.notifications import EbayNotificationStatus
from inventorum.ebay.lib.db.models import BaseModel

from django.db import models
from django_extensions.db.fields.json import JSONField


log = logging.getLogger(__name__)


class EbayNotificationModel(BaseModel):
    """ Stores received ebay notifications for later reference """

    event_type = models.CharField(max_length=255)
    payload = JSONField()

    timestamp = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)

    request_body = models.TextField()

    status = models.CharField(max_length=255, choices=EbayNotificationStatus.CHOICES,
                              default=EbayNotificationStatus.UNHANDLED)
    status_details = models.TextField(null=True, blank=True)

    @classmethod
    def create_from_ebay_notification(cls, notification):
        """
        :type notification: inventorum.ebay.lib.ebay.notifications.EbayNotification
        """
        return cls.objects.create(event_type=notification.event_type,
                                  payload=notification.payload,
                                  timestamp=notification.timestamp,
                                  signature=notification.signature,
                                  request_body=notification.request_body)

    def set_status(self, status, details=None):
        self.status = status
        self.status_details = details

        self.save()
