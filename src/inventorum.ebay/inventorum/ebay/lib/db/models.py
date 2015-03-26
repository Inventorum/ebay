# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

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


class MappedInventorumModel(AbstractModel):
    """
    Base class for inventorum entities that exist outside of the ebay context
    and are mapped into the ebay service by their universal inv_id.
    """

    class Meta:
        abstract = True

    inv_id = models.IntegerField(unique=True, verbose_name="Universal inventorum id")

    def __unicode__(self):
        return "[{} (inv-id: {})] {}".format(self.pk, self.inv_id, self.__class__.__name__)
