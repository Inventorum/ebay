# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import os
import vcr
from django.conf import settings


log = logging.getLogger(__name__)


IntegrationTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR),
    record_mode='once'
)

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
    VALID_IMAGE_ID = 2933
    VALID_IMAGE_2_ID = 2556

    EMAIL = "tech+ebay@inventorum.com"

    COUNTRY = Countries.DE

    class Products:
        # no variations, one image
        SIMPLE_PRODUCT_ID = 1225145632417445479L
        # no variations, one image, and ebay meta
        PRODUCT_WITH_EBAY_META_ID = 1225145633542203515L
        PRODUCT_WITH_SHIPPING_SERVICES = 1225146152575102591L

        PRODUCT_WITH_EAN = 1225145632417445479L
        PRODUCT_WITHOUT_EAN = 1225146152575102591L

        PRODUCT_VALID_FOR_PUBLISHING = 1225146162033178864L
        PRODUCT_NOT_EXISTING = 1

        IPAD_STAND = 1225146588560351744L

        # variations
        PRODUCT_WITH_VARIATIONS_AND_EAN = 1225147276579275043L

        WITH_VARIATIONS_VALID_ATTRS = 1225147276579275043L
        WITH_VARIATIONS_INVALID_ATTRS = 1225147437974515692L
        WITH_VARIATIONS_MISSING_ATTRS = 1225149599816952506L
        WITH_VARIATIONS_NO_ATTRS = 1225149600498410675L

    class OrderableProducts:
        XTC_ADVANCED_2_LTD = 463690
        FAST_ROAD_COMAX = 463691
