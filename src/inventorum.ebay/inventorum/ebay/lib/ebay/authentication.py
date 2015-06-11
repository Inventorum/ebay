# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import EbayTrading
from django.conf import settings
from inventorum.ebay.lib.ebay.data import EbayParser
from inventorum.ebay.lib.ebay.data.authorization import EbayToken


class EbayAuthentication(EbayTrading):
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

        parsed_expiration_time = EbayParser.parse_date(response['HardExpirationTime'])
        token = EbayToken(response['eBayAuthToken'], parsed_expiration_time, site_id=self.default_site_id)

        self.token = token
        self.update_notification_settings()

        return token

    def update_notification_settings(self):
        self.execute('SetNotificationPreferences', {
            "ApplicationDeliveryPreferences": {
                # "ApplicationURL": 'https://app.inventorum.com/v1/ebay/platform-notifications/',
                "ApplicationEnable": "Enable",
                "AlertEnable": "Enable",
                "DeviceType": "Platform",
                'DeliveryURLDetails': [
                    {
                        'DeliveryURL': 'https://ebay-notifications.inventorum.net/api/channel/ebay/notifications/',
                        'DeliveryURLName': 'sandbox',
                        'Status': 'Enable'
                    },
                    {
                        'DeliveryURL': 'https://dev-ebay-notifications.inventorum.net/api/channel/ebay/notifications/',
                        'DeliveryURLName': 'sandbox-dev',
                        'Status': 'Enable'
                    },
                    {
                        'DeliveryURL': 'https://ebay-notifications.inventorum.com/api/channel/ebay/notifications/',
                        'DeliveryURLName': 'live',
                        'Status': 'Enable'
                    },
                    {
                        'DeliveryURL': 'https://ebay-notifications.inventorum.com/v1/ebay/platform-notifications/',
                        'DeliveryURLName': 'oldlive',
                        'Status': 'Enable'
                    },
                    {
                        'DeliveryURL': 'mailto:michal+ebayplatform@inventorum.com',
                        'DeliveryURLName': 'michalemail',
                        'Status': 'Enable'
                    }
                ]
            },
            'DeliveryURLName': 'sandbox,live,oldlive,michalemail',
            'UserDeliveryPreferenceArray': {
                'NotificationEnable': [
                    {
                        'EventType': 'FixedPriceTransaction',
                        # This notification is sent to a subscribed seller each time a
                        # buyer purchases an item (or multiple items in the case of a
                        # multi-quantity listing) in a fixed-price listing.
                        'EventEnable': 'Enable'
                    },
                    {
                        'EventType': 'ItemSold',
                        # This notification is sent to the subscribed seller each time a seller's single-quantity,
                        # fixed-price listing ends with a sale. In the case of a multiple-quantity, fixed-price listing,
                        # the 'FixedPriceTransaction' notification will be sent to the seller instead of 'ItemSold'.
                        'EventEnable': 'Enable'
                    },
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
                        'EventType': 'ItemSuspended',
                        # This notification is sent to the subscribed seller and subscribed potential buyers if eBay
                        # has administratively ended a listing for whatever reason.
                        'EventEnable': 'Enable'
                    },
                ]}
            }
        )
