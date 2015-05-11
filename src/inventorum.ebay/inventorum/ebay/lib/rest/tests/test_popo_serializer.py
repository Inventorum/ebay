# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from datetime import date

from unittest.case import TestCase

from inventorum.ebay.lib.rest.serializers import POPOSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


# Test POPOs #################################################################################

class _Customer(object):
    def __init__(self, first_name, last_name, birthday=None, foo_address=None):
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.foo_address = foo_address


class _Address(object):
    def __init__(self, street, zip_code, city):
        self.street = street
        self.zip_code = zip_code
        self.city = city


class _AddressSerializer(POPOSerializer):

    class Meta:
        model = _Address

    street = serializers.CharField()
    zip_code = serializers.CharField()
    city = serializers.CharField()


class _CustomerSerializer(POPOSerializer):

    class Meta:
        model = _Customer

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    BirthDay = serializers.DateField(source="birthday", required=False)

    address = _AddressSerializer(required=False, source="foo_address")


class _CustomerSerializerWithUndefinedPOPOAttributes(_CustomerSerializer):
    undefined_popo_attribute = serializers.IntegerField()


class _CustomerSerializerWithUndefinedSerializerAttributes(POPOSerializer):

    class Meta:
        model = _Customer


class _Order(object):
    def __init__(self, items):
        self.items = items


class _OrderItem(object):
    def __init__(self, product_id, price, quantity):
        self.product_id = product_id
        self.price = price
        self.quantity = quantity


class _OrderItemSerializer(POPOSerializer):

    class Meta:
        model = _OrderItem

    product_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()


class _OrderSerializer(POPOSerializer):

    class Meta:
        model = _Order

    items = _OrderItemSerializer(many=True)


# Specs ####################################################################################

class TestPOPOSerializer(TestCase):

    def test_serializes_simple_popo(self):
        customer = _Customer("John", "Wayne")
        serializer = _CustomerSerializer(customer)

        self.assertEqual(serializer.data, {
            "first_name": "John",
            "last_name": "Wayne",
            "BirthDay": None,
            "address": None
        })

        customer = _Customer("John", "Wayne", birthday=date(2015, 04, 01))
        serializer = _CustomerSerializer(customer)

        self.assertEqual(serializer.data, {
            "first_name": "John",
            "last_name": "Wayne",
            "BirthDay": "2015-04-01",
            "address": None
        })

    def test_deserializes_simple_popo(self):
        data = {
            "first_name": "John",
            "last_name": "Wayne"
        }

        serializer = _CustomerSerializer(data=data)

        instance = serializer.build()
        self.assertIsInstance(instance, _Customer)
        self.assertEqual(instance.first_name, "John")
        self.assertEqual(instance.last_name, "Wayne")
        self.assertEqual(instance.birthday, None)

        data.update({
            "BirthDay": "2015-04-01"
        })

        serializer = _CustomerSerializer(data=data)
        instance = serializer.build()
        self.assertTrue(instance)
        self.assertEqual(instance.birthday, date(2015, 04, 01))

    def test_serializes_nested_popo(self):
        customer = _Customer("John", "Wayne", foo_address=_Address("Voltastraße 5", "1337", "Berlin"))
        serializer = _CustomerSerializer(customer)

        self.assertEqual(serializer.data, {
            "first_name": "John",
            "last_name": "Wayne",
            "BirthDay": None,
            "address": {
                "street": "Voltastraße 5",
                "zip_code": "1337",
                "city": "Berlin"
            }
        })

    def test_deserializes_nested_popo(self):
        data = {
            "first_name": "John",
            "last_name": "Wayne",
            "address": {
                "street": "Voltastraße 5",
                "zip_code": "1337",
                "city": "Berlin"
            }
        }

        serializer = _CustomerSerializer(data=data)
        instance = serializer.build()
        self.assertTrue(instance)
        self.assertTrue(instance.foo_address)

        address = instance.foo_address
        self.assertEqual(address.street, "Voltastraße 5")
        self.assertEqual(address.zip_code, "1337")
        self.assertEqual(address.city, "Berlin")

    def test_serializes_nested_list_popo(self):
        items = [
            _OrderItem(1, price=D("3.99"), quantity=5),
            _OrderItem(2, price=D("1.00"), quantity=3)
        ] 
        order = _Order(items)
        
        serializer = _OrderSerializer(order)

        self.assertEqual(serializer.data, {
            "items": [
                {
                    "product_id": 1,
                    "price": "3.99",
                    "quantity": 5
                },
                {
                    "product_id": 2,
                    "price": "1.00",
                    "quantity": 3
                }
            ]
        })

    def test_deserializes_nested_list_popo(self):
        data = {
            "items": [
                {
                    "product_id": 23,
                    "price": "0.49",
                    "quantity": 1
                },
                {
                    "product_id": 42,
                    "price": "100.00",
                    "quantity": 4
                }
            ]
        }

        serializer = _OrderSerializer(data=data)

        instance = serializer.build()
        self.assertIsInstance(instance, _Order)
        self.assertEqual(len(instance.items), 2)
        for item in instance.items:
            self.assertIsInstance(item, _OrderItem)

    def test_deserialize_throws_with_additional_attributes(self):
        data = {
            "first_name": "John",
            "last_name": "Wayne",
            "undefined_popo_attribute": 1
        }

        serializer = _CustomerSerializerWithUndefinedPOPOAttributes(data=data)
        with self.assertRaises(ValidationError):
            serializer.build()

    def test_deserialize_throws_with_too_few_serializer_attributes(self):
        data = {
            "first_name": "John",
            "last_name": "Wayne",
        }

        serializer = _CustomerSerializerWithUndefinedSerializerAttributes(data=data)
        with self.assertRaises(ValidationError):
            serializer.build()
