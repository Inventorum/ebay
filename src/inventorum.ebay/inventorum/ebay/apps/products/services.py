# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext
from inventorum.ebay.apps.products.models import EbayProductModel


class PublishingValidationException(Exception):
    pass


class PublishingService(object):
    def __init__(self, core_product):
        """
        Service for publishing products to ebay
        :param core_product: Core product from API
        :return:
        :type core_product: inventorum.ebay.apps.core_api.models.CoreProduct
        """
        self.core_product = core_product
        self.product = self._create_db_product()

    def _create_db_product(self):
        return EbayProductModel.create_from_core_product(self.product)

    def validate(self):
        if self.core_product.is_parent:
            raise PublishingValidationException(ugettext('Cannot publish products with variations'))








