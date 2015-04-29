# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from inventorum.ebay.apps.auth.resources import AuthorizeEbayResource

log = logging.getLogger(__name__)

urlpatterns = patterns('',
                       url(r'^authorize/$', AuthorizeEbayResource.as_view(), name='authorize'),
                       url(r'^logout/$', AuthorizeEbayResource.as_view(), name='logout'),
                       url(r'^success.html$', TemplateView.as_view(template_name='auth/success.html'), name='success-html'),
                       url(r'^failure.html$', TemplateView.as_view(template_name='auth/failure.html'), name='failure-html'),
)
