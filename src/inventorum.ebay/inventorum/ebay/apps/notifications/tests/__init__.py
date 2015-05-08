# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.notifications.fixtures.notification_templates import compile_notification_template


log = logging.getLogger(__name__)


class NotificationTestsMixin(object):

    def post_notification(self, event_type, template, timestamp=None, signature=None, **kwargs):
        data = compile_notification_template(template, timestamp=timestamp, signature=signature, **kwargs)
        headers = dict(CONTENT_TYPE='text/xml; charset="utf-8"', HTTP_SOAPACTION=event_type)
        return self.client.post("/notifications/", data=data, **headers)
