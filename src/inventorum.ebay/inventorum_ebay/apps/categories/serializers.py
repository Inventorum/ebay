# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.apps.categories import models
from inventorum_ebay.apps.categories.models import SpecificValueModel
from rest_framework import serializers


log = logging.getLogger(__name__)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CategoryModel
        fields = ("id", "name", "country", "parent_id", "is_leaf", "variations_enabled", "ean_enabled", "ean_required")

    # Must be added explicitly as rest framework validates fields and does not recognize fields contributed by mptt
    parent_id = serializers.IntegerField()
    variations_enabled = serializers.BooleanField(source="features.variations_enabled")
    ean_enabled = serializers.BooleanField(source="features.ean_enabled")
    ean_required = serializers.BooleanField(source="features.ean_required")


class CategoryBreadcrumbSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CategoryModel
        fields = ("id", "name")


class VerboseCategorySerializer(CategorySerializer):

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ("breadcrumbs",)

    breadcrumbs = CategoryBreadcrumbSerializer(source="ancestors", many=True)


class SpecificValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificValueModel
        fields = ("value", )


class CategorySpecificsSerializer(serializers.ModelSerializer):
    values = SpecificValueSerializer(many=True)

    class Meta:
        model = models.CategorySpecificModel
        fields = ("id", "help_text", "help_url", "can_use_in_variations", "is_required", "can_use_own_values",
                  "values", "min_values", "max_values", "name")


class CategoryListResponseSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    data = CategorySerializer(many=True)
    breadcrumbs = CategoryBreadcrumbSerializer(many=True)


class CategorySuggestionSerializer(serializers.Serializer):
    percent_item_found = serializers.IntegerField()
    category = VerboseCategorySerializer()


class RootedCategorySuggestionsSerializer(serializers.Serializer):
    root = CategorySerializer()
    suggested_categories = CategorySuggestionSerializer(many=True)


class CategorySearchParameterDeserializer(serializers.Serializer):
    query = serializers.CharField()
    limit = serializers.IntegerField(required=False)


class RootedCategorySearchResultSerializer(serializers.Serializer):
    root = CategorySerializer()
    categories = VerboseCategorySerializer(many=True)
