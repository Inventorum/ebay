# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import os
import vcr
from django.conf import settings


log = logging.getLogger(__name__)


CoreApiTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'core_api'),
    record_mode='once'
)

ApiTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'core_api'),
    record_mode='once'
)

MockedTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'mocked'),
    record_mode='once'
)


EbayTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'ebay'),
    record_mode='once',
    filter_headers=['X-EBAY-API-APP-NAME', 'X-EBAY-API-CERT-NAME', 'X-EBAY-API-DEV-NAME', 'Authorization']
)


class Countries:
    DE = "DE"
    AT = "AT"


class StagingTestAccount:
    ACCOUNT_ID = 346
    USER_ID = 425
    TAX_TYPE_19_ID = 1063

    EMAIL = "tech+ebay@inventorum.com"

    COUNTRY = Countries.DE

    class Products:
        # no variations, one image
        SIMPLE_PRODUCT_ID = 463690
        # no variations, one image, and ebay meta
        PRODUCT_WITH_EBAY_META_ID = 463691
        PRODUCT_WITH_SHIPPING_SERVICES = 640416

        PRODUCT_VALID_FOR_PUBLISHING = 640449
        PRODUCT_NOT_EXISTING = 1

        IPAD_STAND = 665753

        #variations
        WITH_VARIATIONS_VALID_ATTRS = 666032
        WITH_VARIATIONS_INVALID_ATTRS = 666407
