# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.data import EbayBooleanField
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, IntegerField

class EbayValueRecommendation(object):
    def __init__(self, value):
        self.value = value


class EbayValueRecommendationSerializer(POPOSerializer):
    Value = CharField(source='value')

    class Meta:
        model = EbayValueRecommendation


class EbaySpecificsNameRecommendationValidationRules(object):
    def __init__(self, max_values=1, min_values=0, can_use_in_variations=True, selection_mode='FreeText', value_type='text'):
        self.max_values = max_values
        self.min_values = min_values
        self.selection_mode = selection_mode
        self.value_type = value_type
        self.can_use_in_variations = can_use_in_variations


class EbaySpecificsNameRecommendationValidationRulesSerializer(POPOSerializer):
    MinValues = IntegerField(source="min_values", required=False)
    MaxValues = IntegerField(source="max_values", required=False)
    SelectionMode = CharField(source="selection_mode", required=False)
    ValueType = CharField(source="value_type", required=False)
    VariationSpecifics = EbayBooleanField(source="can_use_in_variations", required=False)

    class Meta:
        model = EbaySpecificsNameRecommendationValidationRules


class EbaySpecificsNameRecommendation(object):
    def __init__(self, name, validation_rules, value_recommendations=None, help_text=None, help_url=None):
        """
        :type name: unicode | str
        :type help_text: unicode | str
        :type help_url: unicode | str
        """
        self.value_recommendations = value_recommendations or []
        self.name = name
        self.help_text = help_text
        self.help_url = help_url
        self.validation_rules = validation_rules

    @property
    def is_required(self):
        return self.validation_rules.min_values > 0


class EbaySpecificsNameRecommendationSerializer(POPOSerializer):
    Name = CharField(source='name')
    HelpText = CharField(source='help_text', required=False)
    HelpURL = CharField(source='help_url', required=False)
    ValidationRules = EbaySpecificsNameRecommendationValidationRulesSerializer(source='validation_rules')
    ValueRecommendation = EbayValueRecommendationSerializer(source="value_recommendations", many=True, required=False)

    class Meta:
        model = EbaySpecificsNameRecommendation


class EbayCategorySpecifics(object):
    def __init__(self, category_id, name_recommendations):
        """
        :type category_id: int
        :type name_recommendations: list[EbaySpecificsNameRecommendation]
        """
        self.category_id = category_id
        self.name_recommendations = name_recommendations

    @classmethod
    def create_from_data(cls, data):
        serializer = EbayCategorySpecificsSerializer(data=data)
        return serializer.build()


class EbayCategorySpecificsSerializer(POPOSerializer):
    CategoryID = CharField(source='category_id')
    NameRecommendation = EbaySpecificsNameRecommendationSerializer(many=True, source="name_recommendations")

    class Meta:
        model = EbayCategorySpecifics