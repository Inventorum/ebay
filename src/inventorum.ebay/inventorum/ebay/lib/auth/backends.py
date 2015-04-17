# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.accounts.models import EbayAccountModel, EbayUserModel
from inventorum.ebay.lib.utils import int_or_none

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


log = logging.getLogger(__name__)


class TrustedHeaderAuthentication(BaseAuthentication):
    # Note: Django converts custom headers to uppercase, replaces hyphens with underscores and adds the HTTP prefix
    # https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.META
    TRUSTED_ACCOUNT_HEADER = "HTTP_X_INV_ACCOUNT"
    TRUSTED_USER_HEADER = "HTTP_X_INV_USER"

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
        inv_account_id = int_or_none(request.META.get(self.TRUSTED_ACCOUNT_HEADER))
        inv_user_id = int_or_none(request.META.get(self.TRUSTED_USER_HEADER))

        if inv_account_id is None or inv_user_id is None:
            return None

        log.debug("Attempting trusted header authentication: X-Inv-User: %s, X-Inv-Account: %s",
                  inv_user_id, inv_account_id)

        account, c = EbayAccountModel.objects.get_or_create(inv_id=inv_account_id)

        user, created = EbayUserModel.objects.select_related('account') \
            .get_or_create(account=account, inv_id=inv_user_id)

        return user, None
