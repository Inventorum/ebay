# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.lib.ebay.data.categories.specifics import EbaySpecificsNameRecommendationSerializer
from inventorum_ebay.tests.testcases import UnitTestCase


class TestGotDictShouldParseToList(UnitTestCase):
    def test_serializer(self):
        data = {
            'Name': "test",
            'ValidationRules': {

            },
            'ValueRecommendation': {
                'Value': 'one_val'
            }
        }
        serializer = EbaySpecificsNameRecommendationSerializer(data=data)
        obj = serializer.build()
        self.assertEqual(len(obj.value_recommendations), 1)
        self.assertEqual(obj.value_recommendations[0].value, 'one_val')

        data = {
            'Name': "test",
            'ValidationRules': {

            },
            'ValueRecommendation': [
                {'Value': 'one_val'},
                {'Value': 'second_val'}
            ]
        }
        serializer = EbaySpecificsNameRecommendationSerializer(data=data)
        serializer.build()
