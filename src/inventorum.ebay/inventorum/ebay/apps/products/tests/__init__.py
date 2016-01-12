# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from decimal import Decimal as D
from django.utils.functional import cached_property
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, CategorySpecificModel, \
    DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, DurationFactory, CategorySpecificFactory
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.tests import StagingTestAccount


class ProductTestMixin(ShippingServiceTestMixin):

    @cached_property
    def valid_category(self):
        """
        Returns the actual eBay category "Verschiedenes > Sonstiges".
        It does not require an EAN nor any category specifics.

        :rtype: inventorum.ebay.apps.categories.models.CategoryModel
        """
        assert CategoryModel.objects.filter(external_id='171949').count() == 0

        category = CategoryModel.objects.create(external_id='171949',
                                                country=StagingTestAccount.COUNTRY,
                                                name="Verschiedenes > Sonstiges")

        features = CategoryFeaturesModel.objects.create(category=category)
        features.durations.create(value='Days_30')

        return category

    @cached_property
    def valid_category_for_variations(self):
        """
        :return:
        """
        # make sure that this category does not exist in the database
        assert CategoryModel.objects.filter(external_id='57989').count() == 0

        category = CategoryModel.objects.create(external_id='57989',
                                                country=StagingTestAccount.COUNTRY,
                                                name="Hosen")

        features = CategoryFeaturesModel.objects.create(category=category,
                                                        variations_enabled=True)
        features.durations.get_or_create(value='Days_30')

        category.specifics.create(name="Hosengröße", min_values=1, max_values=1)
        category.specifics.create(name="Marke", min_values=1, max_values=1)

        return category

    def assign_product_to_valid_category(self, product):
        """
        Assigns the given product to a valid eBay category
        :type product: EbayProductModel
        """
        product.category = self.valid_category
        product.save()

    def assign_valid_shipping_services(self, product):
        """
        Assigns valid eBay shipping services to the given product
        :type product: EbayProductModel
        """
        product.shipping_services.create(service=self.get_shipping_service_hermes(), cost="4.50",
                                         additional_cost=D("1.00"))
        product.shipping_services.create(service=self.get_shipping_service_dhl(), cost=D("5.00"),
                                         additional_cost=D("3.00"))

    def get_product(self, inv_id, account):
        """
        Returns an eBay product model with given information

        :type inv_id: long
        :type account: inventorum.ebay.apps.accounts.tests.factories.EbayAccountFactory

        :rtype: EbayProductModel
        """
        return EbayProductModel.objects.get_or_create(inv_id=inv_id, account=account)[0]

    def get_valid_ebay_product_for_publishing(self, account, inv_id=None):
        """
        Returns a valid eBay product model for publishing connected to a valid core product of the staging test account

        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :type inv_id: None | long

        :rtype: EbayProductModel
        """
        inv_id = inv_id or StagingTestAccount.Products.IPAD_STAND
        product = self.get_product(inv_id, account)

        self.assign_product_to_valid_category(product)
        self.assign_valid_shipping_services(product)

        return product

    def get_valid_ebay_product_with_variations_for_publishing(self, account, inv_id=None):
        """
        :rtype: EbayProductModel
        """
        inv_id = inv_id or StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS
        product = self.get_product(inv_id, account)

        self.assign_valid_shipping_services(product)

        category = self.valid_category_for_variations
        product.category = category
        product.save()

        product.specific_values.create(specific=category.specifics.get(name="Hosengröße"),
                                       value="33/32")

        product.specific_values.create(specific=category.specifics.get(name="Marke"),
                                       value="Diesel")

        return product
