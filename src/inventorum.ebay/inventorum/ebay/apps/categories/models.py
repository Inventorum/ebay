# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from django.db.models.fields import CharField, BooleanField
from django.utils.translation import ugettext
from django_countries.fields import CountryField
from inventorum.ebay.lib.db.models import MappedInventorumModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


log = logging.getLogger(__name__)


class CategoryModel(MPTTModel):
    """ Represents an ebay category """

    parent = TreeForeignKey('self', null=True, blank=True, related_name="children",
                            verbose_name=ugettext("Parent Category"))
    country = CountryField()
    name = CharField(max_length=255)
    external_id = CharField(max_length=255)  # Ebay documentation says it is string
    external_parent_id = CharField(max_length=255)  # Ebay documentation says it is string
    b2b_vat_enabled = BooleanField(default=False)
    best_offer_enabled = BooleanField(default=False)
    auto_pay_enabled = BooleanField(default=False)
    item_lot_size_disabled = BooleanField(default=False)
    ebay_leaf = BooleanField(default=False)

    @classmethod
    def create_from_ebay_category(cls, data):
        """
        Create CategoryModel out of EbayCategory
        :param data: Raw ebay category
        :return: Category model

        :type data: inventorum.ebay.lib.ebay.data.EbayCategory
        :rtype: CategoryModel | None
        """

        if data.virtual:
            # We cannot create category if it is expired or virtual
            return None

        return CategoryModel.objects.create(
            name=data.name,
            external_id=data.category_id,
            external_parent_id=data.parent_id,
            b2b_vat_enabled=data.b2b_vat_enabled,
            best_offer_enabled=data.best_offer_enabled,
            auto_pay_enabled=data.auto_pay_enabled,
            item_lot_size_disabled=data.item_lot_size_disabled,
        )