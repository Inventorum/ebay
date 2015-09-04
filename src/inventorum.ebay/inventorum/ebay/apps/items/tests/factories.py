from __future__ import absolute_import, unicode_literals
import factory
from factory import fuzzy
from decimal import Decimal
from inventorum.ebay.apps.items import EbaySKU

from inventorum.ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayPicture, EbayPickupInStoreDetails, \
    EbayShippingDetails, EbayShippingServiceOption
from inventorum.ebay.tests import Countries


class EbayFixedPrizeItemFactory(factory.Factory):
    class Meta:
        model = EbayFixedPriceItem

    title = 'testProduct'
    description = '30'
    listing_duration = '30'
    country = Countries.DE
    postal_code = '12345'
    quantity = 1
    start_price = Decimal('1.00')
    paypal_email_address = 'test@inventorum.com'
    payment_methods = ['CreditCard', 'Bar']
    shipping_services = ()
    pictures = [
        EbayPicture(url='http://www.testpicture.de/image.png')]
    shipping_details = EbayShippingDetails(EbayShippingServiceOption(shipping_service='DE_UPSStandard'))
    pick_up = EbayPickupInStoreDetails(is_eligible_for_pick_up=False)
    category_id = factory.Sequence(lambda n: "{0}".format(n))
    item_id = '463690'
    sku = EbaySKU.generate_sku('463690')
