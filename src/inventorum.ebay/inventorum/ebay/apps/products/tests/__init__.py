# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from decimal import Decimal as D
from django.utils.functional import cached_property
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, DurationFactory
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin


class ProductTestMixin(ShippingServiceTestMixin):

    @cached_property
    def valid_category(self):
        category = CategoryFactory.create(external_id='176973')
        category.features.durations.clear()
        category.features.durations.add(DurationFactory.create(value='Days_30'))
        return category

    def assign_product_to_valid_category(self, product):
        product.category = self.valid_category
        product.save()


    def assign_valid_shipping_services(self, product):
        product.shipping_services.create(service=self.get_shipping_service_hermes(), cost="4.50",
                                         additional_cost=D("1.00"))
        product.shipping_services.create(service=self.get_shipping_service_dhl(), cost=D("5.00"),
                                         additional_cost=D("3.00"))

    def get_product(self, inv_product_id, account):
        return EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=account)[0]