# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data.preferences import GetUserPreferencesResponseType


class EbayPreferences(EbayTrading):
    def get_user_preferences(self):
        """
        http://developer.ebay.com/devzone/xml/docs/reference/ebay/GetUserPreferences.html

        :rtype: GetUserPreferencesResponseType
        """
        data = {'ShowSellerProfilePreferences': True}
        response = self.execute('GetUserPreferences', data)
        return GetUserPreferencesResponseType.Deserializer(data=response).build()
