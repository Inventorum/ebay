# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.accounts.models import AddressModel
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.ebay.lib.ebay.info import EbayInfo


class AuthorizationService(object):
    def __init__(self, account, auto_commit=True):
        self.account = account
        self.auto_commit = auto_commit

    def assign_token_from_session_id(self, session_id):
        auth = EbayAuthentication()
        token = auth.fetch_token(session_id)

        db_token = EbayTokenModel.create_from_ebay_token(token)
        self.account.token = db_token
        self._auto_committed_save()

    def fetch_user_data_from_ebay(self):
        """
        Fetch user data from ebay
        :return:

        """
        token = EbayToken(self.account.token.value, self.account.token.expiration_date)
        auth = EbayInfo(token)
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

    def save(self):
        self.account.save()