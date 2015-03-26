# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static

log = logging.getLogger(__name__)


urlpatterns = patterns('',
    url(r'^accounts/', include('inventorum.ebay.apps.accounts.urls', namespace='accounts')),
    url(r'^products/', include('inventorum.ebay.apps.products.urls', namespace='products')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
