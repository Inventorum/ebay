# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum_ebay.apps.products import resources

log = logging.getLogger(__name__)

urlpatterns = patterns('',
    url(r'^publish$', resources.BatchPublishResource.as_view(), name='batch_publish'),
    url(r'^(?P<inv_product_id>[0-9]+$)', resources.EbayProductResource.as_view(), name='categories'),
    url(r'^(?P<inv_product_id>[0-9]+)/publish$', resources.PublishResource.as_view(), name='publish'),
    url(r'^(?P<inv_product_id>[0-9]+)/unpublish$', resources.UnpublishResource.as_view(), name='unpublish'),
)
