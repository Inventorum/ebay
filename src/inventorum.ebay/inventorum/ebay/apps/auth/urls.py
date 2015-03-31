# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum.ebay.apps.auth.resources import AuthorizeEbayResource

log = logging.getLogger(__name__)

urlpatterns = patterns('',
                       url(r'^', AuthorizeEbayResource.as_view(), name='authorize'),
)
