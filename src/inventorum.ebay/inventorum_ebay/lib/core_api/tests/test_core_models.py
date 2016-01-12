# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.lib.core_api import BinaryCoreOrderStates
from inventorum_ebay.lib.core_api.models import CoreOrder, CoreBasket
from inventorum_ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreOrder(UnitTestCase):

    def test_state_properties(self):
        core_order = CoreOrder(id=1, state=(BinaryCoreOrderStates.DRAFT | BinaryCoreOrderStates.PENDING), basket=CoreBasket(items=[]))

        self.assertFalse(core_order.is_paid)
        self.assertFalse(core_order.is_shipped)
        self.assertFalse(core_order.is_closed)
        self.assertFalse(core_order.is_canceled)
        self.assertFalse(core_order.is_delivered)

        core_order.state |= BinaryCoreOrderStates.PAID

        self.assertTrue(core_order.is_paid)
        self.assertFalse(core_order.is_shipped)
        self.assertFalse(core_order.is_closed)
        self.assertFalse(core_order.is_canceled)
        self.assertFalse(core_order.is_delivered)

        core_order.state |= BinaryCoreOrderStates.SHIPPED

        self.assertTrue(core_order.is_paid)
        self.assertTrue(core_order.is_shipped)
        self.assertFalse(core_order.is_closed)
        self.assertFalse(core_order.is_closed)
        self.assertFalse(core_order.is_delivered)

        core_order.state |= BinaryCoreOrderStates.CLOSED

        self.assertTrue(core_order.is_paid)
        self.assertTrue(core_order.is_shipped)
        self.assertTrue(core_order.is_closed)
        self.assertFalse(core_order.is_canceled)
        self.assertFalse(core_order.is_delivered)

        core_order.state = BinaryCoreOrderStates.DRAFT | BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.CANCELED \
                           | BinaryCoreOrderStates.DELIVERED
        self.assertFalse(core_order.is_paid)
        self.assertFalse(core_order.is_shipped)
        self.assertFalse(core_order.is_closed)
        self.assertTrue(core_order.is_canceled)
        self.assertTrue(core_order.is_delivered)
