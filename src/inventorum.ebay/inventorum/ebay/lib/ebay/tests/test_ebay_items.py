# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.tests import EbayTest
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayItemShippingService, EbayPicture
from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from decimal import *


log = logging.getLogger(__name__)


class TestEbayItems(EbayAuthenticatedAPITestCase):

    def _build_wrong_item(self):
        """
        Build item for ebay with missing photos, wrong category_id (not leaf), wrong duration (120 is not supported in
        this category)
        """
        # self, title, description, listing_duration, country, postal_code, quantity, start_price,
        #          paypal_email_address, payment_methods, pictures, category_id, sku=None, shipping_services=(),
        #          item_specifics=None, variations=None, ean=None, is_click_and_collect=False, shipping_details=None,
        #          pick_up=None, variation=None, item_id=None):

        shipping = EbayItemShippingService(
            shipping_id="DE_DHLPaket",
            cost="10"
        )
        picture = EbayPicture(
            url='http://shop.inventorum.com/uploads/img-hash/a9fe/1db9/8c9e/564c/8877/d8a1/f1f8/a9fe1db98c9e564c8877d8'
                'a1f1f8fccf_ipad.JPEG'
        )
        return EbayFixedPriceItem(
            sku="test_321",
            title="Inventorum iPad Stand",
            description="<![CDATA[Stand for iPad from Inventorum for your POS Shop]]>",
            listing_duration="Days_120",
            country="DE",
            postal_code="13355",
            quantity=1,
            start_price=Decimal(599.99),
            paypal_email_address="bartosz@hernas.pl",
            payment_methods=['PayPal'],
            pictures=[picture],
            category_id="64540",
            shipping_services=[shipping]
        )

    def _build_correct_item(self):
        picture = EbayPicture(
            url='http://shop.inventorum.com/uploads/img-hash/a9fe/1db9/8c9e/564c/8877/d8a1/f1f8/a9fe1db98c9e564c8877d8'
                'a1f1f8fccf_ipad.JPEG'
        )
        shipping = EbayItemShippingService(
            shipping_id="DE_DHLPaket",
            cost="5"
        )
        return EbayFixedPriceItem(
            sku="test_124",
            title="Inventorum iPad Stand",
            description="Der stylische iPad-Stand von INVENTORUM aus edlem Holz rundet das Erscheinungsbild Ihrer neuen"
                        " iPad-Kasse optimal ab. Durch seinen speziellen Neigungswinkel ist dieser ideal, um einfach un"
                        "d schnell Produkte mit der internen Kamera des iPads zu scannen.",
            listing_duration="Days_30",
            country="DE",
            postal_code="13355",
            quantity=1,
            start_price=Decimal(45.99),
            paypal_email_address="bartosz@hernas.pl",
            payment_methods=['PayPal'],
            category_id="176973",
            shipping_services=[shipping],
            pictures=[picture]
        )

    @EbayTest.use_cassette("ebay_publish_ipad_stand_no_image.yaml")
    def test_failed_publishing(self):
        item = self._build_wrong_item()
        service = EbayItems(self.ebay_token)
        with self.assertRaises(EbayConnectionException) as e:
            response = service.publish(item)

        errors = e.exception.errors
        self.assertEqual(len(errors), 4)

        self.assertEqual(errors[0].long_message, 'Für diese Kategorie ist kein Artikelzustand verfügbar. '
                                                 'Der eingegebene Artikelzustand wurde entfernt.')
        self.assertEqual(errors[0].short_message, 'Artikelzustand kann nicht verwendet werden.')
        self.assertEqual(errors[0].code, 21917121)
        self.assertEqual(errors[0].severity_code, 'Warning')
        self.assertEqual(errors[0].classification, 'RequestError')

        self.assertEqual(errors[1].long_message, 'Erforderliche Mindesanzahl an Bildern:  1 Für Angebote in dieser '
                                                 'Kategorie empfehlen wir Ihnen, mindestens 2 Fotos hochzuladen, um '
                                                 'Ihre Verkaufschancen  möglicherweise um 12 zu erhöhen. '
                                                 '(Prozentangabe beruht auf Anteilen an verkauften Artikeln in dieser '
                                                 'Kategorie mit unterschiedlich vielen Bildern. Tatsächliche '
                                                 'Ergebnisse können anders ausfallen und der Verkauf ist nicht '
                                                 'garantiert.)')
        self.assertEqual(errors[1].code, 21919136)
        self.assertEqual(errors[1].severity_code, 'Error')
        self.assertEqual(errors[1].classification, 'RequestError')


        self.assertEqual(errors[2].long_message, 'Bei der ausgewählten Kategorie handelt es sich nicht um eine so '
                                                 'genannte Unterkategorie.')
        self.assertEqual(errors[2].code, 87)
        self.assertEqual(errors[2].severity_code, 'Error')
        self.assertEqual(errors[2].classification, 'RequestError')


        self.assertEqual(errors[3].long_message, 'Die Dauer "120" (in Tagen) ist für dieses Angebotsformat nicht '
                                                 'verfügbar, bzw. ungültig für die Kategorie "64540".')
        self.assertEqual(errors[3].code, 83)
        self.assertEqual(errors[3].severity_code, 'Error')
        self.assertEqual(errors[3].classification, 'RequestError')

    @EbayTest.use_cassette("ebay_publish_ipad_stand_correct_then_unpublish_it.yaml")
    def test_publishing(self):
        item = self._build_correct_item()
        service = EbayItems(self.ebay_token)
        response = service.publish(item)
        self.assertTrue(response.item_id)
        self.assertTrue(response.start_time)
        self.assertTrue(response.end_time)

        service = EbayItems(self.ebay_token)
        response = service.unpublish(response.item_id)

        self.assertTrue(response.end_time)


    @EbayTest.use_cassette("ebay_publish_ipad_stand_correct.yaml")
    def test_error_message(self):
        item = self._build_correct_item()
        service = EbayItems(self.ebay_token)

        with self.assertRaises(EbayConnectionException) as e:
            response = service.publish(item)

        self.assertTrue(e.exception.ebay_message)
        self.assertTrue(e.exception.serialized_errors[0]['parameters'])
        params = e.exception.serialized_errors[0]['parameters']
        self.assertTrue(params[0].startswith('<div>'), 'Does not starts with <div>: %s' % params[0])
