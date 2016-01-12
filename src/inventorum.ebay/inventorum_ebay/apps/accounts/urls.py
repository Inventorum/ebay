# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum_ebay.apps.accounts import resources

log = logging.getLogger(__name__)


urlpatterns = patterns('',
    url(r'^$', resources.EbayAccountResource.as_view(), name='details'),
)
