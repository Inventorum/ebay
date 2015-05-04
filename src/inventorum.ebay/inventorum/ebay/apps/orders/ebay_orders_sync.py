# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime
from django.db import transaction
from django.utils.functional import cached_property

from inventorum.ebay.apps.orders import tasks
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemVariationModel
from inventorum.ebay.apps.shipping.models import ShippingServiceModel, ShippingServiceConfigurationModel
from inventorum.ebay.lib.ebay.data import OrderStatusCodeType, TradingRoleCodeType, EbayParser
from inventorum.ebay.lib.ebay.orders import EbayOrders
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from inventorum.util.celery import TaskExecutionContext


log = logging.getLogger(__name__)


class PeriodicEbayOrdersSync(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        assert self.account.is_ebay_authenticated, "Account {} is not authenticated to ebay".format(account)

        self.sync = IncomingEbayOrderSyncer(self.account)

    def run(self):
        current_sync_start = datetime.utcnow()
        # if there was no sync yet, the ebay account creation is taken as starting point
        last_sync_start = self.account.last_ebay_orders_sync or self.account.time_added

        get_orders_response = self._get_completed_orders(mod_time_from=last_sync_start)
        orders = get_orders_response.orders

        log.info("Received {} completed orders from ebay for account {} since {}"
                 .format(len(orders), self.account, last_sync_start))

        for order in orders:
            try:
                self.sync(order)
            except EbayOrderSyncException as e:
                # For now, we simply log errors to see how the sync behaves in production
                # Later, we probably want to or need to create some special error handling for certain cases
                log.error(unicode(e))

        self.account.last_ebay_orders_sync = current_sync_start
        self.account.save()

    def _get_completed_orders(self, mod_time_from):
        """
        :type mod_time_from: datetime
        :rtype: inventorum.ebay.lib.ebay.data.responses.GetOrdersResponseType
        """
        ebay_token = self.account.token.ebay_object
        ebay_api = EbayOrders(token=ebay_token)

        return ebay_api.get_orders({
            "OrderStatus": OrderStatusCodeType.Completed,
            "OrderRole": TradingRoleCodeType.Seller,
            "ModTimeFrom": EbayParser.format_date(mod_time_from),
            "Pagination": {
                "EntriesPerPage": 100  # max value
            }
        })


class EbayOrderSyncException(Exception):
    pass


class IncomingEbayOrderSyncer(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    @cached_property
    def task_execution_context(self):
        return TaskExecutionContext(user_id=self.account.default_user.id,
                                    account_id=self.account.id,
                                    request_id=None)

    @transaction.atomic()
    def __call__(self, ebay_order):
        """
        :type ebay_order: inventorum.ebay.lib.ebay.data.responses.OrderType
        """
        is_new_order = not OrderModel.objects.filter(ebay_id=ebay_order.order_id).exists()
        if is_new_order:
            order_model = self._create_order_model_from_ebay_order(ebay_order)
            tasks.schedule_core_order_creation(order_model.id, context=self.task_execution_context)
        else:
            # Currently, we do not perform any updates since we're only fetching completed orders
            log.info("Order with `ebay_id={}` already exists".format(ebay_order.order_id))

    def _create_order_model_from_ebay_order(self, ebay_order):
        """
        :type ebay_order: inventorum.ebay.lib.ebay.data.responses.OrderType
        """
        model = OrderModel()

        model.account = self.account
        model.ebay_id = ebay_order.order_id
        model.ebay_status = ebay_order.order_status
        model.original_ebay_data = POPOSerializer.extract_original_data(ebay_order)

        # extract buyer information
        buyer = ebay_order.transactions[0].buyer
        model.buyer_first_name = buyer.user_first_name
        model.buyer_last_name = buyer.user_last_name
        model.buyer_email = buyer.email

        shipping_address = ebay_order.shipping_address
        # ebay only returns a name, we distinguish between first and last name
        if " " in shipping_address.name:
            shipping_first_name, shipping_last_name = shipping_address.name.split(" ", 1)
        else:
            shipping_first_name, shipping_last_name = shipping_address.name, ""

        model.shipping_first_name = shipping_first_name
        model.shipping_last_name = shipping_last_name
        model.shipping_address1 = shipping_address.street_1
        model.shipping_address2 = shipping_address.street_2
        model.shipping_city = shipping_address.city_name
        model.shipping_postal_code = shipping_address.postal_code
        model.shipping_state = shipping_address.state_or_province
        model.shipping_country = shipping_address.country

        # extract payment information
        model.payment_amount = ebay_order.amount_paid
        model.payment_method = ebay_order.checkout_status.payment_method
        model.payment_status = ebay_order.checkout_status.payment_status

        # extract order details
        model.subtotal = ebay_order.subtotal
        model.total = ebay_order.total

        model.save()

        # extract shipping information
        selected_shipping = ebay_order.shipping_service_selected

        try:
            service_model = ShippingServiceModel.objects.by_country(self.account.country)\
                .get(external_id=selected_shipping.shipping_service)
        except ShippingServiceModel.DoesNotExist:
            raise EbayOrderSyncException("No matching ShippingServiceModel found with `external_id={}`"
                                         .format(selected_shipping.shipping_service))

        model.selected_shipping = ShippingServiceConfigurationModel.create(service=service_model,
                                                                           cost=selected_shipping.shipping_cost)
        model.save()

        for ebay_transaction in ebay_order.transactions:
            self._create_order_line_item_model_from_ebay_transaction(model, ebay_transaction)

        return model

    def _create_order_line_item_model_from_ebay_transaction(self, order_model, ebay_transaction):
        """
        :type order_model: OrderModel
        :type ebay_transaction: inventorum.ebay.lib.ebay.data.responses.TransactionType
        :rtype: OrderLineItemModel
        """
        try:
            item_model = EbayItemModel.objects.get(external_id=ebay_transaction.item.item_id)
        except EbayItemModel.DoesNotExist as e:
            raise EbayOrderSyncException("No EbayItemModel found with ebay item id {}"
                                         .format(ebay_transaction.item.item_id))

        orderable_item, orderable_name = None, None
        if item_model.has_variations and ebay_transaction.variation:
            # => variation has been bought from multi item listing
            sku = ebay_transaction.variation.sku

            if sku is None:
                raise EbayOrderSyncException("Got ebay transaction for a variation of item (pk: {}) without SKU"
                                             .format(item_model.pk))

            try:
                ebay_variation_model = item_model.variations.by_sku(sku).get()
            except EbayItemVariationModel.DoesNotExist:
                raise EbayOrderSyncException("No EbayItemVariationModel found with SKU {}".format(sku))
            except EbayItemVariationModel.MultipleObjectsReturned:
                raise EbayOrderSyncException("Multiple EbayItemVariationModels found with SKU {}".format(sku))

            orderable_item = ebay_variation_model
            orderable_name = ebay_transaction.variation.variation_title
        elif not item_model.has_variations and not ebay_transaction.variation:
            # => regular item has been bought
            orderable_item = item_model
            orderable_name = ebay_transaction.item.title
        # Exception handling for cases that should never happen but probably will because either we or ebay fucked up :)
        elif not item_model.has_variations and ebay_transaction.variation:
            raise EbayOrderSyncException("Got ebay transaction with variation for an item (pk: {}) "
                                         "without variations".format(item_model.pk))
        elif item_model.has_variations and not ebay_transaction.variation:
            raise EbayOrderSyncException("Got ebay transaction without variation for an item (pk: {}) "
                                         "with variations".format(item_model.pk))

        line_item_model = OrderLineItemModel()

        line_item_model.ebay_id = ebay_transaction.transaction_id
        line_item_model.order = order_model

        line_item_model.orderable_item = orderable_item
        line_item_model.name = orderable_name
        line_item_model.quantity = ebay_transaction.quantity_purchased
        line_item_model.unit_price = ebay_transaction.transaction_price

        line_item_model.save()

        return line_item_model
