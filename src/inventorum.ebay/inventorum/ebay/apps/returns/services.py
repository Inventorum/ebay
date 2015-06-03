# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.data.events import EbayEventReturnedItem, EbayEventReturned
from inventorum.ebay.lib.ebay.events import EbayInboundEvents


log = logging.getLogger(__name__)


class EbayReturnService(object):

    def __init__(self, account, return_model):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :type return_model: inventorum.ebay.apps.returns.models.ReturnModel
        """
        self.account = account
        self.return_model = return_model

    def send_ebay_return_event(self):
        """
        Notifies ebay about the return by sending an inbound EBAY.ORDER.RETURNED event.
        When this method succeeds, the return coming from the core api is considered to be "synced" with ebay.
        """
        assert not self.return_model.synced_with_ebay, "Return {} already synced with ebay".format(self.return_model)

        return_items_for_event = [EbayEventReturnedItem(item_id=return_item.order_line_item.orderable_item.ebay_item_id,
                                                        transaction_id=return_item.order_line_item.transaction_id,
                                                        refund_quantity=return_item.refund_quantity,
                                                        refund_amount=return_item.refund_amount)
                                  for return_item in self.return_model.items.all()]

        event = EbayEventReturned(order_id=self.return_model.order.ebay_id,
                                  refund_amount=self.return_model.refund_amount,
                                  refund_type=self.return_model.refund_type,
                                  refund_note=self.return_model.refund_note,
                                  items=return_items_for_event)

        inbound_events = EbayInboundEvents(self.account.token.ebay_object)
        inbound_events.publish(event, raise_exceptions=True)

        self.return_model.synced_with_ebay = True
        self.return_model.save()
