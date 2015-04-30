# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from random import randint

import factory
from django.db import models

from inventorum.util.django.db.managers import ValidityQuerySet
from inventorum.util.django.db.models import AbstractModel
from inventorum.util.django.model_utils import PassThroughManager


log = logging.getLogger(__name__)


class BaseQuerySet(ValidityQuerySet):
    """ Base class for QuerySets """
    pass


class BaseModel(AbstractModel):
    """ Base class for database models """

    class Meta:
        abstract = True

    objects = PassThroughManager.for_queryset_class(BaseQuerySet)()


class MappedInventorumModelQuerySet(BaseQuerySet):

    def by_inv_id(self, inv_id):
        return self.filter(inv_id=inv_id)


class MappedInventorumModel(BaseModel):
    """
    Base class for inventorum entities that exist outside of the ebay context
    and are mapped into the ebay service by their universal inv_id.
    """

    class Meta:
        abstract = True

    inv_id = models.IntegerField(unique=True, verbose_name="Universal inventorum id")

    objects = PassThroughManager.for_queryset_class(MappedInventorumModelQuerySet)()

    def __unicode__(self):
        return "{} (inv_id: {})".format(self.pk, self.inv_id)


class MappedInventorumModelFactory(factory.DjangoModelFactory):
    # A randomly generated inv_id to better reflect reality
    # TODO jm: Use fuzzy attribute instead
    inv_id = factory.LazyAttribute(lambda m: randint(999, 99999))
