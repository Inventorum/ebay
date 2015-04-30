# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime, timedelta
from django.db import transaction
from inventorum.ebay.lib.ebay.data import OrderStatusCodeType, TradingRoleCodeType, EbayParser
from inventorum.ebay.lib.ebay.orders import EbayOrders


log = logging.getLogger(__name__)


class EbayOrdersSync(object):
    """
    Responsible for fetching *completed* ebay orders and for creating these in our system
    """

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        assert self.account.is_ebay_authenticated, "Account {} is not authenticated to ebay".format(account.id)

    @transaction.atomic()
    def run(self):
        last_sync_time = (datetime.utcnow() - timedelta(days=5))

        ebay_token = self.account.token.ebay_object
        ebay_api = EbayOrders(token=ebay_token)

        get_orders_response = ebay_api.get_orders({
            "OrderStatus": OrderStatusCodeType.Completed,
            "OrderRole": TradingRoleCodeType.Seller,
            "ModTimeFrom": EbayParser.format_date(last_sync_time),
            "Pagination": {
                "EntriesPerPage": 100  # max value
            }
        })

        orders = get_orders_response.orders

        log.info("Received {} new orders from ebay for account {} since {}"
                 .format(len(orders), self.account, last_sync_time))

        import json

        for order in orders:
            buyer = order.transactions[0].buyer
            shipping_address = order.shipping_address

            log.info(getattr(order, "_initial_data", ""))

            log.info(json.dumps({
                "basket": {
                    "items": [{
                        "name": t.item.title,
                        "unit_gross_price": str(t.transaction_price),
                        "quantity": t.quantity_purchased
                    } for t in order.transactions]
                },
                "customer": {
                    "email": buyer.email,
                    "first_name": buyer.user_first_name,
                    "last_name": buyer.user_last_name,
                    "shipping_address": {
                        "address1": shipping_address.street_1,
                        "address2": shipping_address.street_2,
                        "city": shipping_address.city_name,
                        "country": shipping_address.country,
                        "country_name": shipping_address.country_name,
                        "name": shipping_address.name,
                        "state": shipping_address.state_or_province,
                        "zipcode": shipping_address.postal_code
                    }
                },
                "payments": [{
                        "payment_method": order.checkout_status.payment_method,
                        "payment_amount": str(order.amount_paid)
                }],
                "shipment": {
                    "cost": str(order.shipping_service_selected.shipping_cost),
                    "name": order.shipping_service_selected.shipping_service
                }
            }, indent=2))
