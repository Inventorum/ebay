# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum_ebay.lib.rest.fields import MoneyField

from rest_framework import serializers
from inventorum_ebay.tests.testcases import UnitTestCase

log = logging.getLogger(__name__)


class MoneyFieldTestSerializer(serializers.Serializer):
    money = MoneyField()


class TestDeltaEndpointQuantizeProblem(UnitTestCase):
    def test_it(self):

        serializer = MoneyFieldTestSerializer(data={'money': '2000000000.00'})
        valid = serializer.is_valid()
        log.debug(serializer.errors)
        self.assertTrue(valid)
