# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from inventorum.ebay.lib.db.models import MappedInventorumModelFactory

from inventorum.ebay.apps.accounts import models


log = logging.getLogger(__name__)


class EbayAccountFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayAccountModel


class EbayUserFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayUserModel

    account = factory.SubFactory(EbayAccountFactory)
