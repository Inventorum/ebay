# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = 'inventorum.ebay.apps.auth'
    label = 'ebay_auth'
    verbose_name = 'Auth'
