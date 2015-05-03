# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.ebay.data import EbayAmountField, EbayArrayField
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers


log = logging.getLogger(__name__)


class UserType(object):
    """
    Represents the ebay `UserType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/UserType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Email = serializers.CharField(source="email")
        UserFirstName = serializers.CharField(source="user_first_name")
        UserLastName = serializers.CharField(source="user_last_name")

    # / Deserialization ###############

    def __init__(self, email, user_first_name, user_last_name):
        """
        :type email: unicode
        :type user_first_name: unicode
        :type user_last_name: unicode
        """
        self.email = email
        self.user_first_name = user_first_name
        self.user_last_name = user_last_name

UserType.Deserializer.Meta.model = UserType


class AddressType(object):
    """
    Represents the ebay `AddressType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/AddressType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        AddressID = serializers.CharField(source="address_id")
        Name = serializers.CharField(source="name")
        Street1 = serializers.CharField(source="street_1")
        Street2 = serializers.CharField(source="street_2", allow_blank=True, allow_null=True)
        CityName = serializers.CharField(source="city_name")
        PostalCode = serializers.CharField(source="postal_code")
        StateOrProvince = serializers.CharField(source="state_or_province", allow_blank=True, allow_null=True)
        Country = serializers.CharField(source="country")
        CountryName = serializers.CharField(source="country_name")

    # / Deserialization ###############

    def __init__(self, address_id, name, street_1, street_2, city_name, postal_code, state_or_province, country,
                 country_name):
        """
        :param address_id: Unique ID for a user's address in the eBay database. This value can help prevent the need
            to store an address multiple times across multiple orders. The ID changes if a user changes their address.
        :type address_id: unicode

        :param name: User's name for the address
        :type name: unicode

        :type street_1: unicode
        :type street_2: unicode
        :type city_name: unicode
        :type postal_code: unicode
        :type state_or_province: unicode

        :param country: Two-digit code representing the country of the user.
        :type country: unicode

        :type country_name: unicode
        """
        self.address_id = address_id
        self.name = name
        self.street_1 = street_1
        self.street_2 = street_2
        self.city_name = city_name
        self.postal_code = postal_code
        self.state_or_province = state_or_province
        self.country = country
        self.country_name = country_name

AddressType.Deserializer.Meta.model = AddressType


class VariationType(object):
    """
    Represents the ebay `VariationType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/VariationType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        VariationTitle = serializers.CharField(source="variation_title")
        SKU = serializers.CharField(source="sku", required=False)

    # / Deserialization ###############

    def __init__(self, variation_title, sku=None):
        """
        :type variation_title: unicode
        :type sku: unicode | None
        """
        self.variation_title = variation_title
        self.sku = sku

VariationType.Deserializer.Meta.model = VariationType


class ItemType(object):
    """
    Represents the ebay `ItemType`
    http://developer.ebay.com/Devzone/XML/docs/Reference/ebay/types/ItemType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        ItemID = serializers.CharField(source="item_id")
        Title = serializers.CharField(source="title")

    # / Deserialization ###############

    def __init__(self, item_id, title):
        """
        :type item_id: unicode
        :type title: unicode
        """
        self.item_id = item_id
        self.title = title

ItemType.Deserializer.Meta.model = ItemType


class GetItemResponseType(object):
    """
    Represents the ebay `GetItemResponseType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetItem.html#Output
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Item = ItemType.Deserializer(source="item")

    # / Deserialization ###############

    def __init__(self, item):
        """
        :type item: ItemType
        """
        self.item = item

GetItemResponseType.Deserializer.Meta.model = GetItemResponseType


class ShippingServiceOptionType(object):
    """
    Represents the ebay `ShippingServiceOptionsType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/ShippingServiceOptionsType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        ShippingService = serializers.CharField(source="shipping_service")
        ShippingServiceCost = EbayAmountField(source="shipping_cost")

    # / Deserialization ###############

    def __init__(self, shipping_service, shipping_cost):
        """
        :type shipping_service: unicode
        :type shipping_cost: decimal.Decimal
        """
        self.shipping_service = shipping_service
        self.shipping_cost = shipping_cost

ShippingServiceOptionType.Deserializer.Meta.model = ShippingServiceOptionType


class TransactionStatusType(object):
    """
    Represents the ebay `TransactionStatusType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/TransactionStatusType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        CompleteStatus = serializers.CharField(source="complete_status", required=False)

    # / Deserialization ###############

    def __init__(self, complete_status=None):
        """
        :type complete_status: unicode | None
        """
        self.complete_status = complete_status

TransactionStatusType.Deserializer.Meta.model = TransactionStatusType


class TransactionType(object):
    """
    Represents the ebay `TransactionType`
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/TransactionType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        TransactionID = serializers.CharField(source="transaction_id")
        QuantityPurchased = serializers.IntegerField(source="quantity_purchased")
        TransactionPrice = EbayAmountField(source="transaction_price")
        Status = TransactionStatusType.Deserializer(source="status")
        Buyer = UserType.Deserializer(source="buyer")
        Item = ItemType.Deserializer(source="item", required=False)
        Variation = VariationType.Deserializer(source="variation", required=False)
        ShippingServiceSelected = ShippingServiceOptionType.Deserializer(source="shipping_service_selected",
                                                                         required=False)

    # / Deserialization ###############

    def __init__(self, transaction_id, quantity_purchased, transaction_price, status, buyer, item=None, variation=None,
                 shipping_service_selected=None):
        """
        :type transaction_id: unicode
        :type quantity_purchased: int
        :type transaction_price: decimal.Decimal
        :type status: TransactionStatusType
        :type buyer: UserType
        :type item: ItemType
        :type variation: VariationType
        :type shipping_service_selected: ShippingServiceOptionType
        """

        self.transaction_id = transaction_id
        self.quantity_purchased = quantity_purchased
        self.transaction_price = transaction_price
        self.status = status
        self.buyer = buyer
        self.item = item
        self.variation = variation
        self.shipping_service_selected = shipping_service_selected

TransactionType.Deserializer.Meta.model = TransactionType


class GetItemTransactionsResponseType(object):
    """
    Represents the ebay `GetItemTransactionsResponseType` response
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetItemTransactions.html#Output
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Item = ItemType.Deserializer(source="item")
        TransactionArray = EbayArrayField(item_key="Transaction", item_deserializer=TransactionType.Deserializer,
                                          source="transactions")

    # / Deserialization ###############

    def __init__(self, item, transactions):
        """
        :type item: ItemType
        :type transactions: list[TransactionType]
        """
        self.item = item
        self.transactions = transactions

GetItemTransactionsResponseType.Deserializer.Meta.model = GetItemTransactionsResponseType


class CheckoutStatusType(object):
    """
    Represents the ebay `CheckoutStatusType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/CheckoutStatusType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Status = serializers.CharField(source="status")
        PaymentMethod = serializers.CharField(source="payment_method")
        eBayPaymentStatus = serializers.CharField(source="payment_status")

    # / Deserialization ###############

    def __init__(self, status, payment_method, payment_status):
        """
        :type status: unicode
        :type payment_method: unicode
        :type payment_status: unicode
        """
        self.status = status
        self.payment_method = payment_method
        self.payment_status = payment_status

CheckoutStatusType.Deserializer.Meta.model = CheckoutStatusType


class PickupMethodSelectedType(object):
    """
    Represents the ebay `PickupMethodSelectedType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/PickupMethodSelectedType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        # http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/PickupMethodCodeType.html
        PickupMethod = serializers.CharField()
        PickupStoreID = serializers.CharField()
        PickupLocationUUID = serializers.CharField()

    # / Deserialization ###############

    def __init__(self, pickup_method, pickup_store_id, pickup_location_uuid):
        """
        :type pickup_method: unicode
        :type pickup_store_id: unicode
        :type pickup_location_uuid: unicode
        """
        self.pickup_method = pickup_method
        self.pickup_store_id = pickup_store_id
        self.pickup_location_uuid = pickup_location_uuid


class OrderType(object):
    """
    Represents the ebay `OrderType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/OrderType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        # This amount includes the sale price of each line item, shipping and any other charges.
        # It is returned after the buyer has completed checkout (=> CheckoutStatus.Status = Complete)
        OrderID = serializers.CharField(source="order_id")
        OrderStatus = serializers.CharField(source="order_status")
        CheckoutStatus = CheckoutStatusType.Deserializer(source="checkout_status")
        AmountPaid = EbayAmountField(source="amount_paid")
        Total = EbayAmountField(source="total")
        Subtotal = EbayAmountField(source="subtotal")

        TransactionArray = EbayArrayField(source="transactions", item_key="Transaction",
                                          item_deserializer=TransactionType.Deserializer)

        ShippingAddress = AddressType.Deserializer(source="shipping_address")
        ShippingServiceSelected = ShippingServiceOptionType.Deserializer(source="shipping_service_selected")
        PickupMethodSelected = PickupMethodSelectedType.Deserializer(source="pickup_method_selected", required=False)

        # ShippingAddress: AddressType

    # / Deserialization ###############

    def __init__(self, order_id, order_status, checkout_status, amount_paid, total, subtotal, transactions,
                 shipping_address, shipping_service_selected, pickup_method_selected=None):
        """
        :type order_id: unicode
        :type order_status: unicode
        :type checkout_status: CheckoutStatusType

        :type amount_paid: decimal.Decimal
        :type total: decimal.Decimal
        :type subtotal: decimal.Decimal
        :type transactions: list[TransactionType]

        :type shipping_address: AddressType
        :type shipping_service_selected: ShippingServiceOptionType
        :type pickup_method_selected: PickupMethodSelectedType
        """
        self.order_id = order_id
        self.order_status = order_status
        self.checkout_status = checkout_status

        self.amount_paid = amount_paid
        self.total = total
        self.subtotal = subtotal
        self.transactions = transactions

        self.shipping_address = shipping_address
        self.shipping_service_selected = shipping_service_selected
        self.pickup_method_selected = pickup_method_selected

OrderType.Deserializer.Meta.model = OrderType


class PaginationResultType(object):
    """
    Represents the ebay `PaginationResultType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/PaginationResultType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        TotalNumberOfEntries = serializers.IntegerField(source="total_number_of_entries")
        TotalNumberOfPages = serializers.IntegerField(source="total_number_of_pages")

    # / Deserialization ###############

    def __init__(self, total_number_of_entries, total_number_of_pages):
        """
        :param total_number_of_entries: Indicates the total number of entries that could be returned by repeated call
            requests. Returned with a value of 0 if no entries are available.
        :type total_number_of_entries: int

        :param total_number_of_pages: Indicates the total number of pages of data that could be returned by repeated
            requests. Returned with a value of 0 if no pages are available.
        :type total_number_of_pages: int
        """
        self.total_number_of_entries = total_number_of_entries
        self.total_number_of_pages = total_number_of_pages


PaginationResultType.Deserializer.Meta.model = PaginationResultType


class GetOrdersResponseType(object):
    """
    Represents the ebay `GetOrdersResponseType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetOrders.html#Output
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        OrderArray = EbayArrayField(source="orders", item_key="Order", item_deserializer=OrderType.Deserializer)
        PaginationResult = PaginationResultType.Deserializer(source="pagination_result")
        PageNumber = serializers.IntegerField(source="page_number")

    # / Deserialization ###############

    def __init__(self, orders, pagination_result, page_number):
        """
        :type orders: list[OrderType]
        :type pagination_result: PaginationResultType
        :type page_number: int
        """
        self.orders = orders
        self.pagination_result = pagination_result
        self.page_number = page_number

GetOrdersResponseType.Deserializer.Meta.model = GetOrdersResponseType
