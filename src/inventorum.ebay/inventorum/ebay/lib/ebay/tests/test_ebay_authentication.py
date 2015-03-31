# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import vcr
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.tests.testcases import APITestCase


class EbayAuthenticationTest(APITestCase):

    @APITestCase.vcr.use_cassette("ebay_get_session_id")
    def test_getting_session_id(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/synopsis.yaml'):
            auth = EbayAuthentication()
            session_id = auth.get_session_id()