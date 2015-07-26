# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.test.testcases import TestCase

from inventorum.ebay.lib.rest.fields import InvIdField
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers

from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


class FieldsTestPOPO(object):
    def __init__(self, inv_id):
        self.inv_id = inv_id


class FieldsTestSerializer(POPOSerializer):
    class Meta:
        model = FieldsTestPOPO

    inv_id = InvIdField(required=True)


class TestInvIdField(TestCase):

    def test_serialization(self):
        obj = FieldsTestPOPO(inv_id=1225146588560351744L)
        serializer = FieldsTestSerializer(obj)

        self.assertEqual(serializer.data, {
            "inv_id": "1225146588560351744"
        })

    def test_deserialization(self):
        serializer = FieldsTestSerializer(data={
            "inv_id": "1225146588560351744"
        })

        obj = serializer.build()
        self.assertEqual(obj.inv_id, 1225146588560351744L)

    def test_validation(self):
        # test value error
        serializer = FieldsTestSerializer(data={
            "inv_id": "INVALID_VALUE"
        })

        with self.assertRaises(ValidationError) as ctx:
            obj = serializer.build()

        self.assertEqual(ctx.exception.detail, {'inv_id': ['A valid number is required.']})

        # test required error to make sure that default error messages are preserved
        serializer = FieldsTestSerializer(data={})

        with self.assertRaises(ValidationError) as ctx:
            obj = serializer.build()

        self.assertEqual(ctx.exception.detail, {'inv_id': ['This field is required.']})
