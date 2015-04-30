# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy
from inventorum.ebay.lib.db.models import MappedInventorumModelFactory

from inventorum.ebay.apps.accounts import models
from inventorum.ebay.tests import StagingTestAccount


log = logging.getLogger(__name__)


class AddressFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.AddressModel

    name = fuzzy.FuzzyText(length=10)
    street = fuzzy.FuzzyText(length=10)
    street1 = fuzzy.FuzzyText(length=10)
    city = fuzzy.FuzzyText(length=10)
    country = 'DE'
    postal_code = fuzzy.FuzzyText(length=2)


class EbayLocationFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayLocationModel

    name = fuzzy.FuzzyText(length=20)
    latitude = fuzzy.FuzzyDecimal(low=0, high=90, precision=10)
    longitude = fuzzy.FuzzyDecimal(low=0, high=180, precision=10)
    phone = fuzzy.FuzzyText(length=20)
    pickup_instruction = fuzzy.FuzzyText(length=20)
    url = 'http://inventorum.com'
    address = factory.SubFactory(AddressFactory)


class EbayAccountFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayAccountModel

    user_id = fuzzy.FuzzyText(length=10)
    email = factory.Sequence(lambda n: 'test{0}@inventorum.com'.format(n))
    country = StagingTestAccount.COUNTRY


class EbayUserFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayUserModel

    account = factory.SubFactory(EbayAccountFactory)
