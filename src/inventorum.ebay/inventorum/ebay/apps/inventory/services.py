# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

log = logging.getLogger(__name__)

class CoreApiQuantityCheck(object):
    def __init__(self, data):
        """
        Checking if items ebay is asking for are still in stock
        :param data: list of items ebay is asking to check
        :param limit_root_nodes: Limit of how many root nodes we should scrap
        :param only_leaf: If true, it will get only leaf categories
        :param limit: How many categories to download
        :return:
        :type ebay_token: inventorum.ebay.lib.ebay.data.EbayToken
        :type limit_root_nodes: int | None
        :type only_leaf: bool
        :type limit: int
        """