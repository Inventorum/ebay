# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from django.utils.functional import cached_property
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayDay, EbayInterval
from inventorum.ebay.lib.ebay.inventorymanagement import EbayInventoryManagement
from requests.exceptions import HTTPError


class EbayLocationUpdateServiceException(Exception):
    pass


class EbayLocationUpdateService(object):
    def __init__(self, user):
        self.user = user

    @cached_property
    def core_info(self):
        try:
            return self.user.core_api.get_account_info()
        except HTTPError as e:
            raise EbayLocationUpdateService(e.response)

    @property
    def core_account(self):
        return self.core_info.account

    @property
    def location_ebay_object(self):
        return self.user.account.location.get_ebay_location_object(self._get_days_as_ebay_objects())

    def update(self):
        ebay_api = EbayInventoryManagement(self.user.account.token.ebay_object)
        try:
            ebay_api.add_location(self.location_ebay_object)
        except EbayConnectionException as e:
            raise EbayLocationUpdateServiceException(e.message)

    def _get_days_as_ebay_objects(self):
        opening_hours = self.core_account.opening_hours
        opening_hours_by_day = defaultdict(list)

        for h in opening_hours:
            opening_hours_by_day[h.day_of_week].append(h)

        days = []
        for day, values in opening_hours_by_day.iteritems():
            intervals = []
            for value in values:
                interval = EbayInterval(
                    open='%02d:%02d:00' % (value.opens_hour, value.opens_minute),
                    close='%02d:%02d:00' % (value.closes_hour, value.closes_minute),
                )
                intervals.append(interval)
            days.append(EbayDay(day, intervals=intervals))
        return days
