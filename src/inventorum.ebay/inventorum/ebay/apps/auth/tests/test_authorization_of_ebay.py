# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
import pytz
from django.utils.datetime_safe import datetime

from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.tests.testcases import APITestCase

log = logging.getLogger(__name__)


class EbayAuthorizationTest(APITestCase):
    @APITestCase.vcr.use_cassette("ebay_get_session_id.json")
    def test_get_session(self):
        response = self.client.get('/auth/authorize/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'session_id': 'qeUBAA**6ffa1eb714c0a5e3ca06a646ffff843c',
            'url': 'https://signin.ebay.de/ws/eBayISAPI.dll?SignIn&RuName=Inventorum_GmbH-Inventor-9021-4-pbiiw&'
                   'SessID=qeUBAA**6ffa1eb714c0a5e3ca06a646ffff843c'
        })

    def test_fetch_token_failed(self):
        response = self.client.post('/auth/authorize/')
        log.debug('Got response: %s', response.data)
        self.assertEqual(response.status_code, 400)

    @APITestCase.vcr.use_cassette("ebay_fetch_token.json")
    def test_fetch_token(self):
        response = self.client.post('/auth/authorize/', data={
            'session_id': 'qeUBAA**6ffa1eb714c0a5e3ca06a646ffff843c'
        })
        log.debug('Got response: %s', response.data)
        self.assertEqual(response.status_code, 200)

        account = EbayAccountModel.objects.get(pk=self.account.pk)
        ebay_token = account.token

        self.assertTrue(ebay_token)
        self.assertEqual(ebay_token.value,
                         'AgAAAA**AQAAAA**aAAAAA**rp4aVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHlYunD5KLqA+dj6x'
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

        self.assertEqual(account.email, "tech+ebay@inventorum.com")
        self.assertEqual(account.id_verified, False)
        self.assertEqual(account.status, 'Confirmed')
        self.assertEqual(account.user_id, 'newmade')
        self.assertEqual(account.qualifies_for_b2b_vat, False)
        self.assertEqual(account.store_owner, False)
        self.assertEqual(account.registration_date, datetime(2015, 3, 31, 8, 57, 26, tzinfo=pytz.UTC))

        address = account.registration_address
        self.assertEqual(address.name, "John Newman")
        self.assertEqual(address.street, None)
        self.assertEqual(address.street1, None)
        self.assertEqual(address.city, 'default')
        self.assertEqual(address.country, 'DE')
        self.assertEqual(address.postal_code, 'default')