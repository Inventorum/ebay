# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import Ebay
from django.conf import settings
from django.utils.datetime_safe import datetime


class EbayToken(object):
    """
    Data object to keeps expiration time and value
    """
    expiration_time = None
    value = None

    def __init__(self, value, expiration_time):
        self.expiration_time = expiration_time
        self.value = value


class EbayAuthentication(Ebay):
    def get_session_id(self):
        response = self.execute('GetSessionID', {'RuName': settings.EBAY_RUNAME})
        return response['SessionID']

    @classmethod
    def get_url_from_session_id(cls, session_id):
        params = 'SignIn&RuName=%s&SessID=%s' % (settings.EBAY_RUNAME, session_id)
        return '%sws/eBayISAPI.dll?%s' % (settings.EBAY_SIGNIN, params)


    def fetch_token(self, session_id):
        """
        Creates ebay auth token using session_id (had to be already validated in frontend)
        Also updates settings for Ebay Notifications Platform
        :param session_id: Session id that was validated in frontend
        :return: Ebay token

        :type session_id: str | unicode
        :rtype: EbayToken
        """
        response = self.execute('FetchToken', {'SessionID': session_id})

        parsed_expiration_time = self.parse_date(response['HardExpirationTime'])
        token = EbayToken(response['eBayAuthToken'], parsed_expiration_time)

        self.token = token
        self._update_notification_settings()

        return token

    def _update_notification_settings(self):
        # TODO: MH: Do we need some more notifications? Disputes, click & collect etc?
        self.execute('SetNotificationPreferences',
                     {
                         'UserDeliveryPreferenceArray':
                             {'NotificationEnable': [
                                 {
                                     'EventType': 'ItemClosed',
                                     # This notification is sent to all subscribed parties of interest
                                     # when a listing ends in the following three ways:
                                     # An auction listing ends without a winning bidder.
                                     # A fixed-price listing ends with no sales
                                     # A multiple-quantity, fixed-price listing ends with sales, but
                                     # with items still available (Quantity > 0)
                                     'EventEnable': 'Enable'
                                 },
                                 {
                                     'EventType': 'ItemUnsold',
                                     # This notification is sent to a subscribing seller when an
                                     # auction listing ends with no winning bidder or when a
                                     # fixed-price listing ends with no sale(s).
                                     'EventEnable': 'Enable'
                                 },
                                 {
                                     'EventType': 'FixedPriceTransaction',
                                     # This notification is sent to a subscribed seller each time a
                                     # buyer purchases an item (or multiple items in the case of a
                                     # multi-quantity listing) in a fixed-price listing.
                                     'EventEnable': 'Enable'
                                 }
                             ]}
                     }
        )