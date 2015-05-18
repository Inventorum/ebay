# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.products.tests.factories import EbayItemFactory, EbayItemVariationFactory, \
    EbayItemVariationSpecificFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestDuplicatedItemSpecificsInVariation(EbayAuthenticatedAPITestCase):
    def test_doubled_item_specifics(self):
        item = EbayItemFactory.create()
        variation_1 = EbayItemVariationFactory.create(item=item)
        variation_2 = EbayItemVariationFactory.create(item=item)

        EbayItemVariationSpecificFactory.create(name='Color', variation=variation_1, values=['Red'])
        EbayItemVariationSpecificFactory.create(name='Color', variation=variation_2, values=['Blue'])

        EbayItemVariationSpecificFactory.create(name='Material', variation=variation_1, values=['Denim'])
        EbayItemVariationSpecificFactory.create(name='Material', variation=variation_2, values=['Denim'])

        data = item.ebay_object.dict()
        self.assertDictEqual(data['Item']['Variations']['VariationSpecificsSet']['NameValueList'][0], {
            'Name': 'Color',
            'Value': {'Red', 'Blue'}
        })
        self.assertDictEqual(data['Item']['Variations']['VariationSpecificsSet']['NameValueList'][1], {
            'Name': 'Material',
            'Value': 'Denim'  # here we make sure 'Denim' is not doubled
        })