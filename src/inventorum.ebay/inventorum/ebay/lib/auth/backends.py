# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.accounts.models import EbayAccountModel, EbayUserModel
from inventorum.ebay.lib.utils import int_or_none

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


log = logging.getLogger(__name__)


class TrustedHeaderAuthentication(BaseAuthentication):
    AUTHENTICATED_ACCOUNT_HEADER = "X-Inv-Account"
    AUTHENTICATED_USER_HEADER = "X-Inv-User"

    def authenticate(self, request):
        """
        Tries to authenticate the given request by using the trusted header ``X-Inv-Account`` and ``X-Inv-User``.
        These headers are set by the API, which authenticates all external requests before they are forwarded
        by nginx to the ebay service.

        :param request: The incoming http request
        :return: Authenticated account or None if authentication was not attempted

        :type request: django.http.request.HttpRequest
        :rtype: (EbayUserModel, None) | None
        """
        inv_account_id = int_or_none(request.META.get(self.AUTHENTICATED_ACCOUNT_HEADER))
        inv_user_id = int_or_none(request.META.get(self.AUTHENTICATED_USER_HEADER))

        if inv_account_id is None or inv_user_id is None:
            return None

        try:
            account = EbayAccountModel.objects.get(inv_id=inv_account_id)
        except EbayAccountModel.DoesNotExist:
            raise AuthenticationFailed("Account %s not connected to ebay" % inv_account_id)

        user, created = EbayUserModel.objects.select_related('account') \
            .get_or_create(account_id=account.id, inv_id=inv_user_id)

        return user, None
