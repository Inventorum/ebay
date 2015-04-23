# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging


log = logging.getLogger(__name__)


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
