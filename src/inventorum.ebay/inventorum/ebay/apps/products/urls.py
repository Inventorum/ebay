# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum.ebay.apps.products import resources

log = logging.getLogger(__name__)

urlpatterns = patterns('',
    url(r'^(?P<inv_product_id>[0-9]+)/publish$', resources.PublishResource.as_view(), name='publish'),
)
