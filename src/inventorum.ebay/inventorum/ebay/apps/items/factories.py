from __future__ import absolute_import, unicode_literals
import factory
from factory import fuzzy
from decimal import Decimal

from inventorum.ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayPicture, EbayPickupInStoreDetails, \
    EbayShippingDetails, EbayShippingServiceOption
from inventorum.ebay.tests import Countries


class EbayFixedPrizeItemFactory(factory.Factory):
    class Meta:
        model = EbayFixedPriceItem

    inv_product_id = fuzzy.FuzzyInteger(low=1000, high=99999)

    title = 'testProduct'
    country = Countries.DE
    description = '30'
    listing_duration = '30'
    postal_code = '12345'
    quantity = 1
    start_price = Decimal('1.00')
    paypal_email_address = 'test@inventorum.com'
    payment_methods = ['CreditCard', 'Bar']
    shipping_details = EbayShippingDetails(EbayShippingServiceOption(shipping_service='DE_UPSStandard'))
    pictures = [
        EbayPicture(url='http://www.testpicture.de/image.png')]
    pick_up = EbayPickupInStoreDetails(is_eligible_for_pick_up=False)
    category_id = ''
    item_id = '123abc'
