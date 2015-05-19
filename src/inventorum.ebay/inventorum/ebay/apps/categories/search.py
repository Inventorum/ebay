# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import itertools
from django.db.models.query_utils import Q

from inventorum.ebay.apps.categories.models import CategoryModel


log = logging.getLogger(__name__)


class RootedCategorySearchResult(object):

    def __init__(self, root, categories):
        """
        :type root: CategoryModel
        :type categories: list[CategoryModel]
        """
        self.root = root
        self.categories = categories


class CategorySearchService(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def search(self, query, limit=None):
        """
        :type query: unicode
        :type limit: int | None
        :rtype: django.db.models.query.QuerySet
        """
        q = Q(country=self.account.country) & Q(name__icontains=query)
        qs = CategoryModel.objects.leaf_nodes().filter(q)

        # prefetch for performance
        qs = qs.select_related("root")

        if limit is not None:
            qs = qs[:limit]

        return qs

    def search_and_group_results_by_root(self, query, limit=None):
        """
        :type query: unicode
        :type limit: int | None
        :rtype: list[RootedCategorySearchResult]
        """
        categories = self.search(query, limit)
        # this boosts the performance as we avoid root lookups for every single category
        roots_by_tree_id = {root.tree_id: root for root in CategoryModel.objects.root_nodes()}

        # group suggestions by category root
        return [RootedCategorySearchResult(root, list(categories))
                for root, categories in itertools.groupby(categories, lambda c: roots_by_tree_id[c.tree_id])]
