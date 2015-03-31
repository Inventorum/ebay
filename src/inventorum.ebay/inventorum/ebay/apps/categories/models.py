# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from django.utils.translation import ugettext
from inventorum.ebay.lib.db.models import MappedInventorumModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


log = logging.getLogger(__name__)


class CategoryModel(MPTTModel):
    """ Represents an ebay category """

    parent = TreeForeignKey('self', null=True, blank=True, related_name="children",
                                 verbose_name=ugettext("Parent Category"))
