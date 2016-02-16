# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from datetime import timedelta, datetime

import factory
from factory import fuzzy
from inventorum.ebay.apps.auth.models import EbayTokenModel
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
    region = fuzzy.FuzzyText(length=10)
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


class EbayTokenModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = EbayTokenModel

    # randomly generated token in the same format as an actual eBay token
    value = "TEST_AA**AQAAAA**aAAAAA**7zV+Ug**nY+sH76PrBmdj6wVnY+sEZ2PrA2dj6wJk4OmC5KKpAydj6x9nY+seQ**qeUBAA**AAMAAA**K8w7vV+LcRadcdBD8ziMmdCRr/1k8OpEdzlvuNEWspZNp5ydVJw3ZkHG2x3Vp9Qwj3g0hP4rJA9/ENIJfl+Zfee+V62fIbHjbhRSUD7L8/TZqdS8Y1NlNLcfYGJfMJJLBXpYxnhv93C3W/1v8FsiqFBsjl6Zgo9eRyGlzDNPlGKUJQp4m1CLv21GHBf8QN1kz9gVa5uFVknBpZtjZ15bDiCy1vHZ5erjw8vTxFhrqsDYWSabxwCvDd8cRoBvDJxGZYol4I1Su6XtDhjuS5ptf1RvYeKo496IMoAj3aHFNRNWG9mtEC1T8gawBjmhNB54dxbRG1s41lcMhdi+mXHhZj8OxtxG9k0O1xxmJHNXVMeh67uNx/okxspUPMIXjtYR8i55sONunSrAIobxdr+UbNEnrzvUT/fMsqWm3CD4Lcr1rn94KTr4yoTn0wCMEZx5yqR7NiO+XL0QjrKskhJGo/EVK06izKIVOza818A1bRBF/kf4tUrOFqxTBzO3h4F9jMezz37IQFmrMQ4yZ2JQNYtkv+5t7CQhpxHBUzQ/kM/lG521TlLwsSvBfxBPVvX55YRSjtDdPLVP91iICCLYldyJ/ugb64+bHynhCTRbNsD7BDbEVCjBumlHPi02nSNuSQRnwTxSJS8/XG89vpE/rCBIKsEEXjVploEx4OF4GtYX+d0eUhqn7+sHR0U0CwOZko7UpbziHh7kwABCnrSush6HJ6GEDpZJJUwoidskZE131zjadGk0KZrPXPNq56hb+"
    expiration_date = factory.LazyAttribute(lambda m: datetime.now() + timedelta(days=1337))
    site_id = 77  # DE


class EbayAccountFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayAccountModel

    user_id = fuzzy.FuzzyText(length=10)
    email = factory.Sequence(lambda n: 'test{0}@inventorum.com'.format(n))
    country = StagingTestAccount.COUNTRY

    token = factory.SubFactory(EbayTokenModelFactory)

    payment_method_paypal_enabled = True
    payment_method_paypal_email_address = 'info@inventorum.com'
    payment_method_bank_transfer_enabled = False


class EbayUserFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayUserModel

    account = factory.SubFactory(EbayAccountFactory)
