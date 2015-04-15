# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField


class EbayCategorySpecifics(object):
    def __init__(self, category_id):
        self.category_id = category_id

    @classmethod
    def create_from_data(cls, data):
        serializer = EbayCategorySpecificsSerializer(data=data)
        return serializer.build()


class EbayCategorySpecificsSerializer(POPOSerializer):
    CategoryID = CharField(source='category_id')

    class Meta:
        model = EbayCategorySpecifics