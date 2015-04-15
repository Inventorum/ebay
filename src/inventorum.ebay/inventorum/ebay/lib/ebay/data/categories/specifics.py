# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField


class EbaySpecificsNameRecommendation(object):
    def __init__(self, name, help_text=None, help_url=None):
        """
        :type name: unicode | str
        :type help_text: unicode | str
        :type help_url: unicode | str
        """
        self.name = name
        self.help_text = help_text
        self.help_url = help_url


class EbaySpecificsNameRecommendationSerializer(POPOSerializer):
    Name = CharField(source='name')
    HelpText = CharField(source='help_text', required=False)
    HelpURL = CharField(source='help_url', required=False)

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