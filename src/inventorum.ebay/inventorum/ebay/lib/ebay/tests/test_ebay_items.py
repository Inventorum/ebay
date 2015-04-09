# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayShippingService
from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestEbayItems(EbayAuthenticatedAPITestCase):
    def _build_wrong_item(self):
        shipping = EbayShippingService(
            id="DE_DHLPaket",
            cost="10"
        )
        return EbayFixedPriceItem(
            title="Inventorum iPad Stand",
            description="Stand for iPad from Inventorum for your POS Shop",
            listing_duration="Days_120",
            country="DE",
            postal_code="13355",
            quantity="1",
            start_price="599.99",
            paypal_email_address="bartosz@hernas.pl",
            payment_methods=['PayPal'],
            category_id="64540",
            shipping_services=[shipping]
        )
    def _build_correct_item(self):
        shipping = EbayShippingService(
            id="DE_DHLPaket",
            cost="5"
        )
        return EbayFixedPriceItem(
            title="Inventorum iPad Stand",
            description="Stand for iPad from Inventorum for your POS Shop",
            listing_duration="Days_30",
            country="DE",
            postal_code="13355",
            quantity="1",
            start_price="599.99",
            paypal_email_address="bartosz@hernas.pl",
            payment_methods=['PayPal'],
            category_id="176973",
            shipping_services=[shipping]
        )

    @EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_publish_ipad_stand_no_image.json")
    def test_failed_publishing(self):
        item = self._build_wrong_item()
        service = EbayItems(self.ebay_token)
        with self.assertRaises(EbayConnectionException) as e:
            response = service.publish(item)

        errors = e.exception.errors
        self.assertEqual(len(errors), 4)

        self.assertEqual(errors[0].long_message, u'Für diese Kategorie ist kein Artikelzustand verfügbar. '
                                                 u'Der eingegebene Artikelzustand wurde entfernt.')
        self.assertEqual(errors[0].short_message, u'Artikelzustand kann nicht verwendet werden.')
        self.assertEqual(errors[0].code, 21917121)
        self.assertEqual(errors[0].severity_code, 'Warning')
        self.assertEqual(errors[0].classification, 'RequestError')


        self.assertEqual(errors[1].long_message, u'Erforderliche Mindesanzahl an Bildern:  1 Für Angebote in dieser '
                                                 u'Kategorie empfehlen wir Ihnen, mindestens 2 Fotos hochzuladen, um '
                                                 u'Ihre Verkaufschancen  möglicherweise um 12 zu erhöhen. '
                                                 u'(Prozentangabe beruht auf Anteilen an verkauften Artikeln in dieser '
                                                 u'Kategorie mit unterschiedlich vielen Bildern. Tatsächliche '
                                                 u'Ergebnisse können anders ausfallen und der Verkauf ist nicht '
                                                 u'garantiert.)')
        self.assertEqual(errors[1].code, 21919136)
        self.assertEqual(errors[1].severity_code, 'Error')
        self.assertEqual(errors[1].classification, 'RequestError')


        self.assertEqual(errors[2].long_message, u'Bei der ausgewählten Kategorie handelt es sich nicht um eine so '
                                                 u'genannte Unterkategorie.')
        self.assertEqual(errors[2].code, 87)
        self.assertEqual(errors[2].severity_code, 'Error')
        self.assertEqual(errors[2].classification, 'RequestError')


        self.assertEqual(errors[3].long_message, u'Die Dauer "120" (in Tagen) ist für dieses Angebotsformat nicht '
                                                 u'verfügbar, bzw. ungültig für die Kategorie "64540".')
        self.assertEqual(errors[3].code, 83)
        self.assertEqual(errors[3].severity_code, 'Error')
        self.assertEqual(errors[3].classification, 'RequestError')



    @EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_publish_ipad_stand_correct.json")
    def test_publishing(self):
        item = self._build_correct_item()
        service = EbayItems(self.ebay_token)
        try:
            response = service.publish(item)
        except EbayConnectionException as e:
            log.error('Errors: %s', e.message)
