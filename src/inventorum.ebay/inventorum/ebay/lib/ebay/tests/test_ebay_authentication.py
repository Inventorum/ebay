# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import vcr
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.tests.testcases import APITestCase


class EbayAuthenticationTest(APITestCase):

    @APITestCase.vcr.use_cassette("ebay_get_session_id.json")
    def test_getting_session_id(self):
        auth = EbayAuthentication()
        session_id = auth.get_session_id()
        self.assertEqual(session_id, 'qeUBAA**6fedb67514c0a54c79557ca5ffffba74')

    def test_building_url(self):
        url = EbayAuthentication.get_url_from_session_id('SESSION_ID')
        self.assertEqual(url, 'https://signin.ebay.de/ws/eBayISAPI.dll?SignIn&RuName=Inventorum_GmbH-Inventor-9021-4-pbiiw&SessID=SESSION_ID')