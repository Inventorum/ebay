# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import ugettext

from inventorum.ebay.apps.accounts.models import AddressModel
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.lib.ebay.info import EbayInfo
from requests.exceptions import HTTPError

log = logging.getLogger(__name__)


class AuthorizationServiceException(Exception):
    pass


class AuthorizationService(object):
    def __init__(self, user, auto_commit=True):
        self.user = user
        self.account = self.user.account
        self.auto_commit = auto_commit

    @cached_property
    def core_info(self):
        try:
            return self.user.core_api.get_account_info()
        except HTTPError as e:
            log.exception('Could not get account info from API')
            raise AuthorizationServiceException('Could not get account info from API')

    def assign_token_from_session_id(self, session_id):
        country = self.core_info.account.country
        site_id = settings.EBAY_SUPPORTED_SITES.get(country, None)
        if site_id is None:
            raise AuthorizationServiceException(ugettext('Country %(country)s not supported') % {'country': country})

        auth = EbayAuthentication(default_site_id=site_id)
        token = auth.fetch_token(session_id)
        db_token = EbayTokenModel.create_from_ebay_token(token)

        self.account.token = db_token
        self.account.country = country

        self._auto_committed_save()

    def fetch_user_data_from_ebay(self):
        """
        Fetch user data from ebay
        :return:

        """
        auth = EbayInfo(self.account.token.ebay_object)
        user = auth.get_user()

        self.account.email = user.email
        self.account.id_verified = user.id_verified
        self.account.status = user.status
        self.account.user_id = user.user_id
        self.account.qualifies_for_b2b_vat = user.seller_info.qualifies_for_b2b_vat
        self.account.store_owner = user.seller_info.store_owner
        self.account.registration_date = user.registration_date
        self.account.registration_address = AddressModel.create_from_ebay_address(user.registration_address)

        self._auto_committed_save()

    def _auto_committed_save(self):
        if self.auto_commit:
            self.save()

    def logout(self):
        self.account.token = None
        self._auto_committed_save()

    def save(self):
        self.account.save()
