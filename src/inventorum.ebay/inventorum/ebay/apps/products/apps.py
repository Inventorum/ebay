# encoding: utf-8
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'inventorum.ebay.apps.products'

    def ready(self):
        from . import signals  # NOQA
