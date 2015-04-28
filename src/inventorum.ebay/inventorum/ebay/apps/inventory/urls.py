# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum.ebay.apps.inventory import resources

log = logging.getLogger(__name__)

urlpatterns = patterns('',
    url(r'^check/$', resources.SanityCheckResource.as_view(), name='sanity_check'),
)
