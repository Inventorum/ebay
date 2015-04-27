# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.rest.serializers import POPOSerializer


log = logging.getLogger(__name__)


class EbayGetItemResponse(object):
    pass


class EbayGetItemResponseDeserializer(POPOSerializer):

    class Meta:
        model = EbayGetItemResponse


class EbayGetItemTransactionsResponse(object):
    pass


class EbayGetItemTransactionsResponseDeserializer(POPOSerializer):

    class Meta:
        model = EbayGetItemTransactionsResponse
