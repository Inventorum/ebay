# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta

import factory
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.ebay.lib.ebay.details import EbayShippingService


log = logging.getLogger(__name__)


class EbayTokenFactory(factory.Factory):

    class Meta:
        model = EbayToken

    value = "AgAAAA**AQAAAA**aAAAAA**7zV+Ug**nY+sH76PrBmdj6wVnY+sEZ2PrA2dj6wJk4OmC5KKpAydj6x9nY+seQ**qeUBAA**AAMAAA**K8w7vV+LcRadcdBD8ziMmdCRr/1k8OpEdzlvuNEWspZNp5ydVJw3ZkHG2x3Vp9Qwj3g0hP4rJA9/ENIJfl+Zfee+V62fIbHjbhRSUD7L8/TZqdS8Y1NlNLcfYGJfMJJLBXpYxnhv93C3W/1v8FsiqFBsjl6Zgo9eRyGlzDNPlGKUJQp4m1CLv21GHBf8QN1kz9gVa5uFVknBpZtjZ15bDiCy1vHZ5erjw8vTxFhrqsDYWSabxwCvDd8cRoBvDJxGZYol4I1Su6XtDhjuS5ptf1RvYeKo496IMoAj3aHFNRNWG9mtEC1T8gawBjmhNB54dxbRG1s41lcMhdi+mXHhZj8OxtxG9k0O1xxmJHNXVMeh67uNx/okxspUPMIXjtYR8i55sONunSrAIobxdr+UbNEnrzvUT/fMsqWm3CD4Lcr1rn94KTr4yoTn0wCMEZx5yqR7NiO+XL0QjrKskhJGo/EVK06izKIVOza818A1bRBF/kf4tUrOFqxTBzO3h4F9jMezz37IQFmrMQ4yZ2JQNYtkv+5t7CQhpxHBUzQ/kM/lG521TlLwsSvBfxBPVvX55YRSjtDdPLVP91iICCLYldyJ/ugb64+bHynhCTRbNsD7BDbEVCjBumlHPi02nSNuSQRnwTxSJS8/XG89vpE/rCBIKsEEXjVploEx4OF4GtYX+d0eUhqn7+sHR0U0CwOZko7UpbziHh7kwTLZnrSush6HJ6GEDpZJJUwoidskZE7PzjjdGk0KZrPXPNq56hb+"
    expiration_time = factory.LazyAttribute(lambda m: datetime.now() + timedelta(days=1337))
    site_id = 77  # DE


class EbayShippingServiceFactory(factory.Factory):

    class Meta:
        model = EbayShippingService

    id = factory.Sequence(lambda i: "ShippingService_%s" % i)
    description = "Hello, I'm an ebay shipping service"
    valid_for_selling_flow = True

    shipping_time_min = 1
    shipping_time_max = 3

    international = False
    dimensions_required = False
