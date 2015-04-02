# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.util.django.db.managers import ValidityManager
import mptt

from django.db.models.fields import CharField, BooleanField
from django_countries.fields import CountryField
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel


log = logging.getLogger(__name__)


class CategoryTreeManager(TreeManager, ValidityManager):
    pass


class CategoryModel(BaseModel):
    """ Represents an ebay category """

    country = CountryField()
    name = CharField(max_length=255)
    external_id = CharField(max_length=255)  # Ebay documentation says it is string
    external_parent_id = CharField(max_length=255, null=True, blank=True)  # Ebay documentation says it is string
    b2b_vat_enabled = BooleanField(default=False)
    best_offer_enabled = BooleanField(default=False)
    auto_pay_enabled = BooleanField(default=False)
    item_lot_size_disabled = BooleanField(default=False)
    ebay_leaf = BooleanField(default=False)

    tree_objects = CategoryTreeManager()

    @classmethod
    def create_or_update_from_ebay_category(cls, data, country_code):
        """
        Create or (update if already created) CategoryModel out of EbayCategory
        :param data: Raw ebay category
        :return: Category model

        :type data: inventorum.ebay.lib.ebay.data.EbayCategory
        :rtype: CategoryModel
        """

        if data.virtual:
            # We cannot create category if it is expired or virtual
            return None

        defaults = dict(
            name=data.name,
            external_parent_id=data.parent_id,
            b2b_vat_enabled=data.b2b_vat_enabled,
            best_offer_enabled=data.best_offer_enabled,
            auto_pay_enabled=data.auto_pay_enabled,
            item_lot_size_disabled=data.item_lot_size_disabled
        )
        category, created = CategoryModel.objects.get_or_create(
            external_id=data.category_id,
            country=country_code,
            defaults=defaults
        )

        if not created:
            category.update(**defaults)

        return category


# MH: We need to do it like this, because then we can use TreeManager() and also our own validity query set etc!
TreeForeignKey(CategoryModel, blank=True, null=True).contribute_to_class(CategoryModel, 'parent')
mptt.register(CategoryModel, order_insertion_by=['name'])