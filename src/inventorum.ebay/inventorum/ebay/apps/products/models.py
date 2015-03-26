# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from inventorum.ebay.lib.db.models import MappedInventorumModel


log = logging.getLogger(__name__)


class EbayProductModel(MappedInventorumModel):
    """ Represents an inventorum product in the ebay context """
    account = models.ForeignKey('accounts.EbayAccountModel', related_name='products',
                                verbose_name="Inventorum ebay account")
