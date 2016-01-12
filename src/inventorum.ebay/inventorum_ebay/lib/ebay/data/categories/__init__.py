# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, IntegerField, BooleanField


class EbayCategory(object):
    name = None
    parent_id = 0
    category_id = 0
    level = 0
    b2b_vat_enabled = False
    best_offer_enabled = False
    auto_pay_enabled = False
    leaf = False
    item_lot_size_disabled = False
    virtual = False
    expired = False
    item_specifics_enabled = False

    def __init__(self, name, parent_id, category_id, level=None, auto_pay_enabled=False, best_offer_enabled=False,
                 item_lot_size_disabled=False, virtual=False, expired=False, leaf=False, b2b_vat_enabled=False,
                 item_specifics_enabled=False):
        self.name = name
        self.parent_id = parent_id
        self.category_id = category_id
        self.level = level
        self.b2b_vat_enabled = b2b_vat_enabled
        self.best_offer_enabled = best_offer_enabled
        self.auto_pay_enabled = auto_pay_enabled
        self.leaf = leaf
        self.item_lot_size_disabled = item_lot_size_disabled
        self.virtual = virtual
        self.expired = expired
        self.item_specifics_enabled = item_specifics_enabled


    @property
    def can_publish(self):
        return not self.expired

    @classmethod
    def create_from_data(cls, data):
        """
        Create Ebay category from json data
        :param data:
        :return: EbayCategory
        :rtype: EbayCategory
        :type data: dict
        """
        serializer = EbayCategorySerializer(data=data)
        return serializer.build()


class EbayCategorySerializer(POPOSerializer):
    CategoryName = CharField(source='name')
    CategoryParentID = CharField(source='parent_id')
    CategoryID = CharField(source='category_id')
    CategoryLevel = IntegerField(source='level', required=False)
    B2BVATEnabled = BooleanField(source='b2b_vat_enabled', required=False)
    BestOfferEnabled = BooleanField(source='best_offer_enabled', required=False)
    AutoPayEnabled = BooleanField(source='auto_pay_enabled', required=False)
    LeafCategory = BooleanField(source='leaf', required=False)
    LSD = BooleanField(source='item_lot_size_disabled', required=False)
    Virtual = BooleanField(source='virtual', required=False)
    Expired = BooleanField(source='expired', required=False)

    class Meta:
        model = EbayCategory

    def validate(self, data):
        if data['parent_id'] == data['category_id']:
            data['parent_id'] = None
        return data
