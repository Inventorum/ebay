# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static

log = logging.getLogger(__name__)


urlpatterns = patterns('',
    url(r'^account/', include('inventorum.ebay.apps.accounts.urls', namespace='accounts')),
    url(r'^auth/', include('inventorum.ebay.apps.auth.urls', namespace='auth')),
    url(r'^products/', include('inventorum.ebay.apps.products.urls', namespace='products')),
    url(r'^categories/', include('inventorum.ebay.apps.categories.urls', namespace='categories')),
    url(r'^inventory/', include('inventorum.ebay.apps.inventory.urls', namespace='inventory')),
    url(r'^shipping/', include('inventorum.ebay.apps.shipping.urls', namespace='shipping')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
