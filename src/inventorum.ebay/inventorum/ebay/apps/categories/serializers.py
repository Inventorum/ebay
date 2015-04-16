# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.categories import models
from rest_framework import serializers


log = logging.getLogger(__name__)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CategoryModel
        fields = ("id", "name", "country", "parent_id", "is_leaf")

    # Must be added explicitly as rest framework validates fields and does not recognize fields contributed by mptt
    parent_id = serializers.IntegerField()


class CategoryBreadcrumbSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CategoryModel
        fields = ("id", "name")


class CategoryListResponseSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    data = CategorySerializer(many=True)
    breadcrumbs = CategoryBreadcrumbSerializer(many=True)
