# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.tests.testcases import UnitTestCase
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory

from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient


log = logging.getLogger(__name__)


class TestEbayUserModel(UnitTestCase):

    def setUp(self):
        self.inv_user_id = 23
        self.inv_account_id = 42
        self.subject = EbayUserFactory.build(inv_id=self.inv_user_id,
                                             account__inv_id=self.inv_account_id)

    def test_instance_has_core_api(self):
        self.assertIsInstance(self.subject.core_api, UserScopedCoreAPIClient)
        self.assertEqual(self.subject.core_api.user_id, self.subject.inv_id)
        self.assertEqual(self.subject.core_api.account_id, self.subject.account.inv_id)
