# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
from django.conf import settings
import vcr


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