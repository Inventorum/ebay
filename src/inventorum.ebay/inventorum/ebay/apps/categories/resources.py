# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.translation import gettext
from inventorum.ebay.apps.categories.models import CategoryModel, CategorySpecificModel
from inventorum.ebay.apps.categories.serializers import CategorySerializer, CategoryBreadcrumbSerializer, \
    CategoryListResponseSerializer, CategorySpecificsSerializer

from inventorum.ebay.lib.rest.exceptions import NotFound
from inventorum.ebay.lib.rest.resources import APIResource

from rest_framework.response import Response


log = logging.getLogger(__name__)


class CategoryListResponse(object):
    def __init__(self, total, data, breadcrumbs):
        self.total = total
        self.data = data
        self.breadcrumbs = breadcrumbs


class CategoryListResource(APIResource):
    serializer_class = CategoryListResponseSerializer

    def get(self, request):
        parent_id = request.query_params.get('parent_id', None)
        country = request.user.account.country

        if parent_id is not None:
            try:
                parent = CategoryModel.objects.get(pk=parent_id, country=country)
            except CategoryModel.DoesNotExist:
                raise NotFound(gettext("Invalid parent_id"), key="categories.invalid_parent_id")

            categories = parent.get_children()
            ancestors = parent.get_ancestors(include_self=True)
        else:
            categories = CategoryModel.objects.root_nodes().filter(country=country)
            ancestors = []

        obj = CategoryListResponse(
            total=categories.count(),
            data=categories,
            breadcrumbs=ancestors
        )
        serializer = self.get_serializer(obj)
        return Response(data=serializer.data)


class CategorySpecificsResponse(APIResource):
    serializer_class = CategorySpecificsSerializer

    def get_queryset(self):
        country = self.request.user.account.country
        return CategoryModel.objects.filter(country=country)

    def get(self, request, pk):
        category = self.get_object()
        serializer = self.get_serializer(category.specifics.all(), many=True)
        return Response(data=serializer.data)
