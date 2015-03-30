# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.conf import settings

from inventorum.ebay.tests.testcases import UnitTestCase

from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient

log = logging.getLogger(__name__)


class TestUserScopedCoreAPIClient(UnitTestCase):

    def setUp(self):
        super(TestUserScopedCoreAPIClient, self).setUp()

        self.user_id = 42
        self.account_id = 23

        self.subject = UserScopedCoreAPIClient(user_id=self.user_id, account_id=self.account_id)

    def test_default_headers(self):
        expected_version = settings.VERSION

        self.assertEqual(self.subject.default_headers, {
            "User-Agent": "inv-ebay/{version}".format(version=expected_version),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Inv-User": unicode(self.user_id),
            "X-Inv-Account": unicode(self.account_id)
        })
