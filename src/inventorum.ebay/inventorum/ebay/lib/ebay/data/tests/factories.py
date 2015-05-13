# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy
from decimal import Decimal as D
from inventorum.ebay.lib.ebay.data import OrderStatusCodeType, CompleteStatusCodeType, PaymentStatusCodeType, \
    BuyerPaymentMethodCodeType
from inventorum.ebay.lib.ebay.data.categories import EbayCategory
from inventorum.ebay.lib.ebay.data.categories.suggestions import SuggestedCategoryType, \
    GetSuggestedCategoriesResponseType
from inventorum.ebay.lib.ebay.data.responses import OrderType, UserType, AddressType, TransactionType, \
    CheckoutStatusType, TransactionStatusType, ItemType, ShippingServiceOptionType, VariationType, GetOrdersResponseType, \
    PaginationResultType


log = logging.getLogger(__name__)


NUMBER_CHARS = [str(i) for i in range(10)]


class UserTypeFactory(factory.Factory):
    
    class Meta:
        model = UserType

    email = fuzzy.FuzzyText(length=5, suffix="@example.com")
    user_first_name = "John"
    user_last_name = "Doe"


class AddressTypeFactory(factory.Factory):

    class Meta:
        model = AddressType

    address_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    name = "John Doe"
    street_1 = "Voltrastraße 5"
    street_2 = None
    city_name = "Berlin"
    postal_code = "13355"
    state_or_province = None
    country = "DE"
    country_name = "Deutschland"


class ShippingServiceOptionTypeFactory(factory.Factory):
    
    class Meta:
        model = ShippingServiceOptionType

    shipping_service = "DE_DHLPaket"
    shipping_cost = D("4.90")


class ItemTypeFactory(factory.Factory):
    
    class Meta:
        model = ItemType

    item_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    title = "Inventorum T-Shirt"


class VariationTypeFactory(factory.Factory):

    class Meta:
        model = VariationType

    variation_title = "Inventorum T-Shirt [M, Black]"
    sku = fuzzy.FuzzyText(length=5, chars=NUMBER_CHARS)


class TransactionStatusTypeFactory(factory.Factory):

    class Meta:
        model = TransactionStatusType

    complete_status = CompleteStatusCodeType.Complete


class TransactionTypeFactory(factory.Factory):

    class Meta:
        model = TransactionType

    transaction_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    quantity_purchased = 1
    transaction_price = fuzzy.FuzzyDecimal(low=1, high=1000)
    status = factory.SubFactory(TransactionStatusTypeFactory)
    buyer = factory.SubFactory(UserTypeFactory)
    item = factory.SubFactory(ItemTypeFactory)


class TransactionTypeWithVariationFactory(TransactionTypeFactory):

    class Meta:
        model = TransactionType

    variation = factory.SubFactory(VariationTypeFactory)


class CheckoutStatusTypeFactory(factory.Factory):
    
    class Meta:
        model = CheckoutStatusType

    status = CompleteStatusCodeType.Complete
    payment_method = BuyerPaymentMethodCodeType.PayPal
    payment_status = PaymentStatusCodeType.NoPaymentFailure


class OrderTypeFactory(factory.Factory):

    class Meta:
        model = OrderType

    order_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    order_status = OrderStatusCodeType.Completed
    checkout_status = factory.SubFactory(CheckoutStatusTypeFactory)

    amount_paid = fuzzy.FuzzyDecimal(low=1, high=1000)
    total = fuzzy.FuzzyDecimal(low=1, high=1000)
    subtotal = fuzzy.FuzzyDecimal(low=1, high=1000)

    @factory.lazy_attribute
    def transactions(self):
        return [TransactionTypeFactory.create()]

    shipping_address = factory.SubFactory(AddressTypeFactory)
    shipping_service_selected = factory.SubFactory(ShippingServiceOptionTypeFactory)


class PaginationResultTypeFactory(factory.Factory):

    class Meta:
        model = PaginationResultType

    total_number_of_entries = 1
    total_number_of_pages = 1


class GetOrdersResponseTypeFactory(factory.Factory):

    class Meta:
        model = GetOrdersResponseType

    page_number = 1
    pagination_result = factory.SubFactory(PaginationResultTypeFactory)

    @factory.lazy_attribute
    def orders(self):
        return [OrderTypeFactory.create()]


class CategoryTypeFactory(factory.Factory):

    class Meta:
        model = EbayCategory

    name = "Handys"
    parent_id = "15032"
    category_id = "48163"


class SuggestedCategoryTypeFactory(factory.Factory):

    class Meta:
        model = SuggestedCategoryType

    category = factory.SubFactory(CategoryTypeFactory)
    percent_item_found = 50


class GetSuggestedCategoriesResponseTypeFactory(factory.Factory):

    class Meta:
        model = GetSuggestedCategoriesResponseType

    category_count = 0
    suggested_categories = []
