# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.core.exceptions import MultipleObjectsReturned
from django.db.models.fields.related import OneToOneField, ManyToManyField, ForeignKey
from inventorum.ebay.apps.categories import ListingDurations
from inventorum.util.django.db.managers import ValidityManager
import mptt

from django.db.models.fields import CharField, BooleanField, URLField, TextField, IntegerField
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
    external_id = CharField(max_length=255, unique_for_date="deleted_at")  # Ebay documentation says it is string
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
            item_lot_size_disabled=data.item_lot_size_disabled,
            ebay_leaf=data.leaf
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


class DurationModel(BaseModel):
    value = CharField(max_length=255, unique_for_date="deleted_at")


class PaymentMethodModel(BaseModel):
    value = CharField(max_length=255, unique_for_date="deleted_at")


class CategoryFeaturesModel(BaseModel):
    category = OneToOneField(CategoryModel, related_name="features")
    durations = ManyToManyField(DurationModel, related_name="features")
    payment_methods = ManyToManyField(PaymentMethodModel, related_name="features")
    item_specifics_enabled = BooleanField(default=False)

    @property
    def max_listing_duration(self):
        ordered_durations = ListingDurations.ORDERED
        durations_values = [d.value for d in self.durations.all()]
        for ordered_duration in ordered_durations:
            if ordered_duration in durations_values:
                return ordered_duration
        return None

    @classmethod
    def create_or_update_from_ebay_data_for_category(cls, data, category):
        """
        Create or update (if it already exists) CategoryFeaturesModel out of EbayFeature instance
        :param data: EbayFeature instance
        :return:
        :type data: inventorum.ebay.lib.ebay.data.features.EbayFeature
        """

        durations_for_fixed_price = data.get_duration_list_by_type('FixedPriceItem')
        durations_db = []
        for duration_name in durations_for_fixed_price:
            duration, c = DurationModel.objects.get_or_create(value=duration_name)
            durations_db.append(duration)

        payment_methods_db = []
        for payment_method in data.payment_methods:
            payment, c = PaymentMethodModel.objects.get_or_create(value=payment_method)
            payment_methods_db.append(payment)

        features, c = cls.objects.get_or_create(category=category)
        features.durations = durations_db
        features.payment_methods = payment_methods_db
        features.item_specifics_enabled = data.details.item_specifics_enabled
        features.save()
        return features


class CategorySpecificModel(BaseModel):
    category = ForeignKey(CategoryModel, related_name="specifics")

    name = CharField(max_length=255)
    help_text = TextField(blank=True, null=True)
    help_url = URLField(null=True, blank=True)

    can_use_in_variations = BooleanField(default=True)
    max_values = IntegerField()
    min_values = IntegerField()
    selection_mode = CharField(max_length=255)
    value_type = CharField(max_length=255)

    class Meta:
        unique_together = ('category', 'name', 'deleted_at')
        ordering = ('name', 'time_added', 'pk')

    @property
    def is_required(self):
        return self.min_values > 0

    @classmethod
    def create_or_update_from_ebay_data_for_category(cls, data, category):
        """
        Create or update (if it already exists) CategoryFeaturesModel out of EbayFeature instance
        :param data: EbayCategorySpecifics instance
        :return: List of CategorySpecificModel
        :rtype: list[CategorySpecificModel]
        :type data: inventorum.ebay.lib.ebay.data.categories.specifics.EbayCategorySpecifics
        """
        specifics = []
        for recommendation in data.name_recommendations:
            defaults = dict(
                help_text=recommendation.help_text,
                help_url=recommendation.help_url,
                can_use_in_variations=recommendation.validation_rules.can_use_in_variations,
                max_values=recommendation.validation_rules.max_values,
                min_values=recommendation.validation_rules.min_values,
                selection_mode=recommendation.validation_rules.selection_mode,
                value_type=recommendation.validation_rules.value_type,
            )
            specific, c = cls.objects.get_or_create(category=category, name=recommendation.name, defaults=defaults)
            if not c:
                specific.__dict__.update(defaults)
                specific.save()
            old_values_ids = {v.pk for v in specific.values.all()}
            current_values = []
            for value in recommendation.value_recommendations:
                value_obj, c = SpecificValueModel.objects.get_or_create(value=value.value, specific=specific)
                current_values.append(value_obj)

            values_to_be_deleted = old_values_ids - set(current_values)

            if values_to_be_deleted:
                SpecificValueModel.objects.filter(pk__in=values_to_be_deleted).delete()

            specifics.append(specific)

        return specifics


class SpecificValueModel(BaseModel):
    value = CharField(max_length=255)
    specific = ForeignKey(CategorySpecificModel, related_name="values")

    class Meta:
        ordering = ('time_added', 'pk')