# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from inventorum.ebay.apps.categories.models import CategoryModel

from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory
from inventorum.ebay.apps.products.serializers import EbayProductCategorySerializer, EbayProductSerializer
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.tests import Countries
from inventorum.ebay.apps.shipping.tests import ShippingServiceConfigurableSerializerTest
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestEbayCategorySerializer(UnitTestCase):

    def test_serialize(self):
        root_category = CategoryFactory.create(name="Root category")
        level_2_category = CategoryFactory.create(name="Level 2 category", parent=root_category)
        leaf_category = CategoryFactory.create(name="Leaf category", parent=level_2_category)

        CategorySpecificFactory.create(category=leaf_category)
        CategorySpecificFactory.create_required(category=leaf_category)

        self.assertEqual(leaf_category.specifics.count(), 2)
        subject = EbayProductCategorySerializer(leaf_category)

        data = subject.data
        specifics = data.pop('specifics')
        self.assertTrue(specifics)
        
        self.assertEqual(data, {
            "id": leaf_category.id,
            "name": "Leaf category",
            "country": "DE",
            "parent_id": level_2_category.id,
            "is_leaf": True,
            "variations_enabled": False,
            "breadcrumb": [
                {"id": root_category.id, "name": "Root category"},
                {"id": level_2_category.id, "name": "Level 2 category"}
            ]
        })


class TestEbayProductSerializer(UnitTestCase, ShippingServiceConfigurableSerializerTest):

    # Required interface for ShippingServiceConfigurableSerializerTest

    def get_serializer_class(self):
        return EbayProductSerializer

    def get_entity(self):
        return EbayProductFactory.create()

    # / Required interface for ShippingServiceConfigurableSerializerTest

    def get_default_category(self):
        some_parent = CategoryFactory.create(name="Some parent")
        return CategoryFactory.create(name="Some category", parent=some_parent)

    def get_default_product(self):
        product = EbayProductFactory.create(category=self.get_default_category())
        product.shipping_services.create(service=self.get_shipping_service_dhl(),
                                         cost=D("5.00"),
                                         additional_cost=D("0.49"))
        return product

    def test_serialize(self):
        product = self.get_default_product()
        category = product.category
        shipping_service = product.shipping_services.first()

        subject = EbayProductSerializer(product)
        self.assertEqual(subject.data, {
            "id": product.id,
            "listing_url": None,
            "is_published": False,
            "category": {
                "id": category.id,
                "name": "Some category",
                "country": "DE",
                "parent_id": category.parent_id,
                "is_leaf": True,
                "variations_enabled": False,
                "breadcrumb": [{"id": category.parent_id, "name": "Some parent"}],
                "specifics": []
            },
            "specific_values": [],
            "shipping_services": [{
                "service": shipping_service.service.id,
                "external_id": "DE_DHLPaket",
                "cost": "5.00",
                "additional_cost": "0.49"
            }]
        })

    def test_deserialize_serialized(self):
        product = self.get_default_product()
        serialized = EbayProductSerializer(product).data

        subject = EbayProductSerializer(product, data=serialized)
        subject.is_valid(raise_exception=True)
        subject.save()

        updated_product = product.reload()

        # deserialize serialized doesn't change the representation
        data_before = serialized
        self.assertEqual(EbayProductSerializer(updated_product).data, data_before)

    def test_category_validation(self):
        def get_partial_data_for_category_update(category):
            return {
                "category": {
                    "id": category.id
                }
            }

        root_category = CategoryFactory.create(name="Root category")
        level_2_category = CategoryFactory.create(name="Level 2 category", parent=root_category)
        leaf_category = CategoryFactory.create(name="Leaf category", parent=level_2_category)

        product = EbayProductFactory(category=None)

        # try to assign category without id
        invalid_data = {"category": {}}
        subject = EbayProductSerializer(product, data=invalid_data, partial=True)
        self.assertFalse(subject.is_valid())
        self.assertEqual(subject.errors["category"], ['id is required'])

        # try to assign non-existing category
        non_persistent_category = CategoryFactory.build(id=999999)
        invalid_data = get_partial_data_for_category_update(non_persistent_category)
        subject = EbayProductSerializer(product, data=invalid_data, partial=True)
        self.assertFalse(subject.is_valid())
        self.assertEqual(subject.errors["category"], ['Invalid pk "999999" - object does not exist.'])

        # try to assign non-leaf categories
        for category in [root_category, level_2_category]:
            invalid_data = get_partial_data_for_category_update(category)
            subject = EbayProductSerializer(product, data=invalid_data, partial=True)
            self.assertFalse(subject.is_valid())
            self.assertEqual(subject.errors["category"], ["Given category is not a leaf"])

        valid_data = get_partial_data_for_category_update(leaf_category)
        assert leaf_category.is_leaf_node()
        subject = EbayProductSerializer(product, data=valid_data, partial=True)
        subject.is_valid(raise_exception=True)

        # try to assign categories from different country
        assert product.account.country != Countries.AT
        leaf_category.country = Countries.AT
        leaf_category.save()
        leaf_category_different_country = leaf_category

        invalid_data = get_partial_data_for_category_update(leaf_category_different_country)
        subject = EbayProductSerializer(product, data=invalid_data, partial=True)
        self.assertFalse(subject.is_valid())
        self.assertEqual(subject.errors["category"], ["Invalid category"])

    def test_cannot_update_categories(self):
        # Note: This test basically only proves that `RelatedModelByIdField` works as expected
        # and can be safely removed when there are separate tests for this field.
        product = EbayProductFactory()
        parent_category = CategoryFactory.create(name="Some parent")
        category = CategoryFactory.create(name="Some category", parent=parent_category)

        assert category.country == Countries.DE

        data = {
            "category": {
                "id": category.id,
                "name": "UPDATED NAME",
                "country": Countries.AT
            }
        }

        subject = EbayProductSerializer(product, data=data, partial=True)
        subject.is_valid(raise_exception=True)
        subject.save()

        # assignment works...
        updated_product = product.reload()
        self.assertEqual(updated_product.category_id, category.id)

        # ...but the category must not be changed
        category = CategoryModel.objects.get(id=category.id)
        self.assertEqual(category.name, "Some category")
        self.assertEqual(category.country, Countries.DE)
