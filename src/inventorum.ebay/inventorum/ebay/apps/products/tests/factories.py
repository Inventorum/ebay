# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta
from decimal import Decimal

import factory
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.lib.db.models import MappedInventorumModelFactory
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.products import models, EbayItemPublishingStatus
from inventorum.ebay.tests import StagingTestAccount


log = logging.getLogger(__name__)


class EbayProductModelFactory(MappedInventorumModelFactory):
    class Meta:
        model = models.EbayProductModel

    account = factory.SubFactory(EbayAccountFactory)


class EbayItemVariationSpecificValueFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.EbayItemVariationSpecificValueModel


class EbayItemVariationSpecificFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Specific 1')

    class Meta:
        model = models.EbayItemVariationSpecificModel

    @factory.post_generation
    def values(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extracted:
            extracted = ['Value 1', 'Value 2']

        for value in extracted:
            EbayItemVariationSpecificValueFactory.create(
                value=value,
                specific=self
            )


class EbayItemVariationFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayItemVariationModel

    inv_product_id = factory.Sequence(lambda n: 2000 + n)
    gross_price = Decimal("1.99")
    tax_rate = Decimal("19")
    quantity = 10


class EbayProductFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayProductModel

    account = factory.SubFactory(EbayAccountFactory)
    inv_id = factory.Sequence(lambda n: 1225147276579271239L + n)


# TODO: Shipping services etc.
class EbayItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = EbayItemModel

    account = factory.SubFactory(EbayAccountFactory)
    product = factory.SubFactory(EbayProductFactory)
    inv_product_id = factory.Sequence(lambda n: 1000 + n)

    category = factory.SubFactory(CategoryFactory)

    name = "Some product listed on ebay"
    description = "Some product description"

    gross_price = Decimal("1.99")
    tax_rate = Decimal("19")
    quantity = 10

    listing_duration = "Days_14"
    paypal_email_address = "foo@example.com"

    country = StagingTestAccount.COUNTRY


class PublishedEbayItemFactory(EbayItemFactory):
    external_id = "1002"
    publishing_status = EbayItemPublishingStatus.PUBLISHED

    @factory.lazy_attribute
    def published_at(self):
        return datetime.utcnow() - timedelta(days=1)

    @factory.lazy_attribute
    def ends_at(self):
        return datetime.utcnow() + timedelta(days=13)


class EbayProductSpecificFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayProductSpecificModel


class EbayItemVariationUpdateFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayItemVariationUpdateModel

    quantity = 1
    gross_price = Decimal("1.99")


class EbayItemUpdateFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayItemUpdateModel

    item = factory.SubFactory(PublishedEbayItemFactory)
    quantity = 1
    gross_price = Decimal("1.99")
