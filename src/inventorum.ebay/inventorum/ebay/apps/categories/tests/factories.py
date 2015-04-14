# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from inventorum.ebay.apps.categories import models


log = logging.getLogger(__name__)


class CategoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.CategoryModel

    name = factory.Sequence(lambda n: "Category {0}".format(n))
    country = "DE"
    parent = None

    external_id = factory.Sequence(lambda n: "{0}")

    @factory.lazy_attribute_sequence
    def external_parent_id(self, n):
        """ Sets the external parent id only when there is a parent """
        if self.parent is not None:
            return n
