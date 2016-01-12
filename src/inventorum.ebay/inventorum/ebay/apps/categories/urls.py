# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from inventorum.ebay.apps.categories import resources


log = logging.getLogger(__name__)


urlpatterns = patterns('',
    url(r'^$', resources.CategoryListResource.as_view(), name='list'),
    url(r'^suggestions$', resources.CategorySuggestionsResource.as_view(), name="suggestions"),
    url(r'^search', resources.CategorySearchResource.as_view(), name="search"),
    url(r'^(?P<pk>[0-9]+)/specifics$', resources.CategorySpecificsResponse.as_view(), name='specifics'),
)
