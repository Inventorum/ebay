# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging


log = logging.getLogger(__name__)


class StagingTestAccount(object):
    ACCOUNT_ID = 346
    USER_ID = 425

    class Products(object):
        # no variations, one image
        SIMPLE_PRODUCT_ID = 463690
        # no variations, one image, and ebay meta
        PRODUCT_WITH_EBAY_META_ID = 463691
        PRODUCT_WITH_SHIPPING_SERVICES = 640416

        PRODUCT_VALID_FOR_PUBLISHING = 640449
        PRODUCT_NOT_EXISTING = 1
