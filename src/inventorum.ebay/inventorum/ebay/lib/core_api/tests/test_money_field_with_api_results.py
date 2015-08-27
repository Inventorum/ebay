# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.fields import MoneyField

from rest_framework import serializers
from inventorum.ebay.tests.testcases import UnitTestCase


class MoneyFieldTestSerializer(serializers.Serializer):
    money = MoneyField()


class TestDeltaEndpointQuantizeProblem(UnitTestCase):
    def test_it(self):
        serializer = MoneyFieldTestSerializer(data={'money': '2000000000.00'})
        self.assertFalse(serializer.is_valid())
