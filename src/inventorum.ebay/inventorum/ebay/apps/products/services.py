# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel


class PublishingValidationException(Exception):
    pass


class PublishingService(object):
    def __init__(self, product_id, user):
        """
        Service for publishing products to ebay
        :param core_product: Core product from API
        :return:
        :type core_product: inventorum.ebay.apps.core_api.models.CoreProduct
        :type account: EbayAccountModel
        """
        self.user = user
        self.core_product = self.user.core_api.get_product(product_id)
        self.core_account = self.user.core_api

    def _create_db_item(self):
        return EbayItemModel.create_from_core_product(self.core_product)

    def validate(self):
        if self.core_product.is_parent:
            raise PublishingValidationException(ugettext('Cannot publish products with variations'))

        if not self.core_product.shipping_services:
            raise PublishingValidationException(ugettext('Product has not shipping services selected'))

        db_product_exists = EbayProductModel.objects.filter(inv_id=self.core_product.id).exists()
        if not db_product_exists:
            raise PublishingValidationException(ugettext('Couldnt find product [inv_id:%s] in database') % self.core_product.id)

    def prepare(self):
        item = self._create_db_item()








