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

class EbayItemVariationModel(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayItemVariationModel


class EbayProductFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayProductModel

    account = factory.SubFactory(EbayAccountFactory)


# TODO: Shipping services etc.
class EbayItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = EbayItemModel

    account = factory.SubFactory(EbayAccountFactory)
    product = factory.SubFactory(EbayProductFactory)
    category = factory.SubFactory(CategoryFactory)

    name = "Some product listed on ebay"
    description = "Some product description"

    gross_price = Decimal("1.99")
    quantity = 10

    listing_duration = "Days_14"
    paypal_email_address = "foo@example.com"

    country = StagingTestAccount.COUNTRY


class PublishedEbayItemFactory(EbayItemFactory):
    external_id = "1002"
    publishing_status=EbayItemPublishingStatus.PUBLISHED

    @factory.lazy_attribute
    def published_at(self):
        return datetime.utcnow() - timedelta(days=1)

    @factory.lazy_attribute
    def ends_at(self):
        return datetime.utcnow() + timedelta(days=13)


class EbayProductSpecificFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayProductSpecificModel


class EbayItemUpdateFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayItemUpdateModel

    item = factory.SubFactory(PublishedEbayItemFactory)
    quantity = 1
    gross_price = Decimal("1.99")
