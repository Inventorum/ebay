# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.shipping.tests import ShippingServiceConfigurableSerializerTest
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestEbayAccountSerializer(UnitTestCase, ShippingServiceConfigurableSerializerTest):

    # Required interface for ShippingServiceConfigurableSerializerTest

    def get_serializer_class(self):
        return EbayAccountSerializer

    def get_entity(self):
        return EbayAccountFactory.create()

    # / Required interface for ShippingServiceConfigurableSerializerTest
