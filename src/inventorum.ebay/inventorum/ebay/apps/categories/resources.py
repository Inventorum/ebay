# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.translation import gettext
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.apps.categories.serializers import CategorySerializer, CategoryBreadcrumbSerializer

from inventorum.ebay.lib.rest.exceptions import NotFound
from inventorum.ebay.lib.rest.resources import APIResource

from rest_framework.response import Response


log = logging.getLogger(__name__)


class CategoryListResource(APIResource):

    def get(self, request):
        parent_id = request.GET.get('parent_id', None)

        if parent_id is not None:
            try:
                parent = CategoryModel.objects.get(pk=parent_id)
            except CategoryModel.DoesNotExist:
                raise NotFound(gettext("Invalid parent_id"), key="categories.invalid_parent_id")

            categories = parent.get_children()
            ancestors = parent.get_ancestors(include_self=True)
        else:
            categories = CategoryModel.objects.root_nodes()
            ancestors = []

        return Response(data={
            "total": categories.count(),
            "data": CategorySerializer(categories, many=True).data,
            "breadcrumb": CategoryBreadcrumbSerializer(ancestors, many=True).data
        })
