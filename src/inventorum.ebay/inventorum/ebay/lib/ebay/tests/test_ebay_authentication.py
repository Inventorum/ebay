# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.datetime_safe import datetime
from inventorum.ebay.apps.core_api.tests import MockedTest
import vcr
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.tests.testcases import APITestCase


class EbayAuthenticationTest(APITestCase):

    @MockedTest.use_cassette("ebay_get_session_id.yaml")
    def test_getting_session_id(self):
        auth = EbayAuthentication()
        session_id = auth.get_session_id()
        self.assertEqual(session_id, 'qeUBAA**6ffa1eb714c0a5e3ca06a646ffff843c')

    def test_building_url(self):
        url = EbayAuthentication.get_url_from_session_id('SESSION_ID')
        self.assertEqual(url, 'https://signin.ebay.de/ws/eBayISAPI.dll?SignIn&RuName='
                              'Inventorum_GmbH-Inventor-9021-4-pbiiw&SessID=SESSION_ID')

    @MockedTest.use_cassette("ebay_fetch_token.yaml")
    def test_fetch_token(self):
        auth = EbayAuthentication()
        token = auth.fetch_token('qeUBAA**6ffa1eb714c0a5e3ca06a646ffff843c')
        self.assertEqual(token.value, 'AgAAAA**AQAAAA**aAAAAA**rp4aVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHlYunD5KLqA+dj6x'
                                      '9nY+seQ**qeUBAA**AAMAAA**O2lrsU8I6yjrricneQO018oJ2GChsYf5PaV62oYlcDgguiGB/IPq89c'
                                      'LIHfiHXjsz5ONAxNsjSzR+elJQkx6NlF+LTw0p3DdPItRFahsbY3O5+iVksmJr++E1+QF7PvkudovYA'
                                      'b183wTZpnZ8np7bsOPAWvFeuRZHbVmwvROSGDQOsAzbWFyVF/6l9xJpHAKULDMzR/nnaCnE24tiTn0V2'
                                      'KH+iBAMZzVbuoXM1kEtIll+N6S0JEvvhtTUW8qlmM0blGaXC7uVfd8CeLDudxEi7T2CSLzsqszuzf+fz'
                                      'BsbSHmAWLWwndHmgnhqyrOXoDrrL9bd2w8jAgO5Lg58/2LoEPbo7TzFXlqv6RPjr0A/gp2/rpbbTl5XT'
                                      'sApPyUN+YiYHuZe0MzxJxgDD6BsGKFK4FmeL+GoC8J9qox5Rk8ynGFOdpjTT29c9gA0NRW0x3iA9zzB5'
                                      'O81Z20+euQJ1L58iVFOcDSHbN2pae0kgafUVJsq96yBz7EB56q9jt1KegCbGXVUrkfCzDUrEmZuJCm3'
                                      'qw6edh6Xir6x+esSnG65toiF/TuiyyC76UYVXctEFxmJFpHbEOou8fzfEHq4FR8LFM5xEmqsx4tUKUFR'
                                      'oxO6pCWHEjPEeOu5Hgl8/JxWDSp/JmTgGwofeIHrgHLJsnA6bhoo6heiAo2O8bGw/sReKccSGNV8JlFZ'
                                      'JXCL7leA3APeVt3yi4itCaSCq0JsDpILTCAdC6vnUEQHcVvowhzN7ck1qmY0gUcOo6IOMuJlxn/')

        self.assertEqual(token.expiration_time, datetime(2016, 9, 21, 13, 18, 38))