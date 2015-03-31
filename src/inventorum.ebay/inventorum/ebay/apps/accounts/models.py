# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from django.db.models.fields import DateTimeField
from django_extensions.db.fields.encrypted import EncryptedTextField
from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient

from inventorum.ebay.lib.auth.models import AuthenticableModelMixin
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel


log = logging.getLogger(__name__)


class EbayAccountModel(MappedInventorumModel):
    """ Represents an inventorum account in the ebay context """
    ebay_token = models.ForeignKey("auth.EbayToken", null=True, blank=True, related_name="accounts", verbose_name="Ebay token")


class EbayUserModel(MappedInventorumModel, AuthenticableModelMixin):
    """ Represents an inventorum user in the ebay context """
    account = models.ForeignKey(EbayAccountModel, related_name="users", verbose_name="Account")

    @property
    def core_api(self):
        """
        :return: User-scoped core api client
        :rtype: UserScopedCoreAPIClient
        """
        return UserScopedCoreAPIClient(user_id=self.inv_id, account_id=self.account.inv_id)
