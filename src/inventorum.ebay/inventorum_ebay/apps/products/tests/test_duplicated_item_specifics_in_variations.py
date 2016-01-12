# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.apps.products.tests.factories import EbayItemFactory, EbayItemVariationFactory, \
    EbayItemVariationSpecificFactory
from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestDuplicatedItemSpecificsInVariation(EbayAuthenticatedAPITestCase):
    def test_doubled_item_specifics(self):
        item = EbayItemFactory.create()
        variation_1 = EbayItemVariationFactory.create(item=item)
        variation_2 = EbayItemVariationFactory.create(item=item)

        EbayItemVariationSpecificFactory.create(name='color', variation=variation_1, values=['Red'])
        EbayItemVariationSpecificFactory.create(name='color', variation=variation_2, values=['Blue'])

        EbayItemVariationSpecificFactory.create(name='material', variation=variation_1, values=['Denim'])
        EbayItemVariationSpecificFactory.create(name='material', variation=variation_2, values=['Denim'])

        data = item.ebay_object.dict()
        self.assertDictEqual(data['Item']['Variations']['VariationSpecificsSet']['NameValueList'][0], {
            'Name': 'Farbe (*)',
            'Value': ['Blue', 'Red']
        })
        self.assertDictEqual(data['Item']['Variations']['VariationSpecificsSet']['NameValueList'][1], {
            'Name': 'Material (*)',
            'Value': 'Denim'  # here we make sure 'Denim' is not doubled
        })
