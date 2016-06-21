# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta
from decimal import Decimal

import factory
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayInterval, EbayDay, EbayLocation
from inventorum.ebay.lib.ebay.data.shipping import EbayShippingService


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


class EbayIntervalFactory(factory.Factory):
    class Meta:
        model = EbayInterval

    open = '08:00:00'
    close = '10:00:00'


class EbayDayFactory(factory.Factory):
    class Meta:
        model = EbayDay

    day_of_week = 1
    intervals = [EbayIntervalFactory.build()]


class EbayLocationFactory(factory.Factory):
    class Meta:
        model = EbayLocation

    location_id = "test_inventorum_location"
    address1 = "Voltrastr 5"
    address2 = "Gebaude 2"
    city = "Berlin"
    country = "DE"
    latitude = Decimal("37.374488")
    longitude = Decimal("-122.032876")
    name = "Test location Inventorum"
    phone = "072 445 78 75"
    pickup_instruction = "Pick it up as soon as possible"
    postal_code = "13355"
    region = "Berlin"
    url = "http://inventorum.com"
    utc_offset = "+02:00"
    days = [EbayDayFactory.build()]
