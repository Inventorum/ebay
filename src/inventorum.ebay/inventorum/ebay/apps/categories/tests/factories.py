# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from inventorum.ebay.apps.categories import models
from inventorum.ebay.tests import StagingTestAccount


log = logging.getLogger(__name__)


class CategoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.CategoryModel
        django_get_or_create = ("name", "country")

    name = factory.Sequence(lambda n: "Category {0}".format(n))
    country = StagingTestAccount.COUNTRY
    parent = None

    external_id = factory.Sequence(lambda n: "{0}")

    @factory.lazy_attribute_sequence
    def external_parent_id(self, n):
        """ Sets the external parent id only when there is a parent """
        if self.parent is not None:
            return n


class SpecificValueFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SpecificValueModel

    value = factory.Sequence(lambda n: "Value {0}".format(n))


class CategorySpecificFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.CategorySpecificModel

    name = factory.Sequence(lambda n: "Specific {0}".format(n))
    help_text = "Some help text"
    help_url = "http://ebay.com/help_url"

    can_use_in_variations = True
    max_values = 1
    min_values = 0
    selection_mode = "FreeText"
    value_type = "Text"

    @factory.post_generation
    def values(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for value in extracted:
                self.values.add(value)
        else:
            for i in range(0, 5):
                SpecificValueFactory.create(specific=self)

    @classmethod
    def create_required(cls, **kwargs):
        return cls.create(min_values=1, **kwargs)
