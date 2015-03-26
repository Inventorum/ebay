# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models

from inventorum.ebay.lib.auth.models import AuthenticableModelMixin
from inventorum.ebay.lib.db.models import MappedInventorumModel


log = logging.getLogger(__name__)


class EbayAccountModel(MappedInventorumModel):
    """ Represents an inventorum account in the ebay context """
    pass


class EbayUserModel(MappedInventorumModel, AuthenticableModelMixin):
    """ Represents an inventorum user in the ebay context """
    account = models.ForeignKey(EbayAccountModel, related_name="users", verbose_name="Account")
