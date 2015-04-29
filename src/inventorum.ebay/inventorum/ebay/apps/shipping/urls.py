# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum.ebay.apps.shipping import resources


log = logging.getLogger(__name__)


urlpatterns = patterns('',
    url(r'^services$', resources.ShippingServiceListResource.as_view(), name='services'),
)
