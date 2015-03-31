# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import Ebay
from django.conf import settings


class EbayAuthentication(Ebay):

    def get_session_id(self):
        response = self.execute('GetSessionID', {'RuName': settings.EBAY_RUNAME})
        print response
        return response['SessionID']

    @classmethod
    def get_url_from_session_id(cls, session_id):
        params = 'SignIn&RuName=%s&SessID=%s' % (settings.EBAY_RUNAME, session_id)
        return '%sws/eBayISAPI.dll?%s' % (settings.EBAY_SIGNIN, params)

