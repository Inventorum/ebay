# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.utils.translation import gettext
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.apps.categories.search import CategorySearchService
from inventorum.ebay.apps.categories.serializers import CategoryListResponseSerializer, CategorySpecificsSerializer, \
    RootedCategorySuggestionsSerializer, CategorySearchParameterDeserializer, RootedCategorySearchResultSerializer
from inventorum.ebay.apps.categories.suggestions import CategorySuggestionsService

from inventorum.ebay.lib.rest.exceptions import NotFound
from inventorum.ebay.lib.rest.resources import APIResource
from rest_framework.exceptions import ValidationError

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


class CategorySearchResource(APIResource):
    serializer_class = RootedCategorySearchResultSerializer

    def get(self, request):
        parameter_serializer = CategorySearchParameterDeserializer(data=request.GET)
        parameter_serializer.is_valid(raise_exception=True)

        service = CategorySearchService(account=self.request.user.account)
        rooted_results = service.search_and_group_results_by_root(query=parameter_serializer.validated_data["query"],
                                                                  limit=parameter_serializer.validated_data.get("limit"))

        serializer = self.get_serializer(rooted_results, many=True)
        return Response(data=serializer.data)


class CategorySuggestionsResource(APIResource):
    serializer_class = RootedCategorySuggestionsSerializer

    def get(self, request):
        query = request.GET.get("query")
        if not query:
            raise ValidationError("Missing query parameter")

        service = CategorySuggestionsService(account=self.request.user.account)
        rooted_suggestions = service.get_suggestions_by_category_root(query)

        serializer = self.get_serializer(rooted_suggestions, many=True)
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
