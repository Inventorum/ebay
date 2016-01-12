# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from django.utils.functional import cached_property
from inventorum_ebay.lib.ebay import EbayConnectionException
from inventorum_ebay.lib.ebay.data.inventorymanagement import EbayDay, EbayInterval
from inventorum_ebay.lib.ebay.inventorymanagement import EbayInventoryManagement
from requests.exceptions import HTTPError


class EbayLocationUpdateServiceException(Exception):
    pass


class EbayLocationUpdateService(object):
    def __init__(self, user):
        self.user = user

    @property
    def can_be_saved(self):
        return self.user.account.has_location and self.core_account.settings.ebay_click_and_collect

    @cached_property
    def core_info(self):
        try:
            return self.user.core_api.get_account_info()
        except HTTPError as e:
            raise EbayLocationUpdateServiceException(e.response)

    @property
    def core_account(self):
        """
        :rtype: inventorum_ebay.apps.core_api.models.CoreAccount
        """
        return self.core_info.account

    @property
    def location_ebay_object(self):
        return self.user.account.location.get_ebay_location_object(self._get_days_as_ebay_objects())

    def update(self):
        ebay_api = EbayInventoryManagement(self.user.account.token.ebay_object)
        try:
            ebay_api.add_location(self.location_ebay_object)
        except EbayConnectionException as e:
            message = "{message}\n{errors}".format(message=e.message,
                                                   errors="\n".join([unicode(err) for err in e.errors]))
            raise EbayLocationUpdateServiceException(message)

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
