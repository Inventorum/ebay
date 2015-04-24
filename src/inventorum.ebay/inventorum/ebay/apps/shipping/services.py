# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.conf import settings
from django.db import transaction
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.lib.ebay.details import EbayDetails


log = logging.getLogger(__name__)


class EbayShippingScraper(object):
    """ Responsible for scraping ebay shipping details """

    def __init__(self, ebay_token):
        """
        :type ebay_token: inventorum.ebay.lib.ebay.data.authorization.EbayToken
        """
        self.ebay_token = ebay_token

    def scrape(self):
        """ Scrapers gonna scrape """
        # the token is mutated for each country => will be reset afterwards
        original_side_id = self.ebay_token.site_id

        for country_code in settings.EBAY_SUPPORTED_SITES.keys():
            with transaction.atomic():
                self._scrape_for_country(country_code)

        self.ebay_token.site_id = original_side_id

    def _scrape_for_country(self, country_code):
        """
        :type country_code: unicode
        """
        ebay_token = self._get_ebay_token_for_country(country_code)
        api = EbayDetails(ebay_token)

        scraped_service_pks = []
        for service in api.get_shipping_services():
            if self._skip(service):
                continue

            db_model = ShippingServiceModel.create_or_update_from_ebay_shipping_service(service, country_code)
            scraped_service_pks.append(db_model.pk)

        removed_services = ShippingServiceModel.objects.by_country(country_code).exclude(pk__in=scraped_service_pks)
        removed_count = removed_services.count()

        removed_services.delete()

        log.info("Scraped {scraped_count} shipping services for {country}, deleted {removed_count}"
                 .format(country=country_code,
                         scraped_count=ShippingServiceModel.objects.filter(country=country_code).count(),
                         removed_count=removed_count))

    def _skip(self, service):
        """
        :type service: inventorum.ebay.lib.ebay.details.EbayShippingService
        :rtype: bool
        """
        return not service.valid_for_selling_flow or service.dimensions_required

    def _get_ebay_token_for_country(self, country_code):
        """
        :type country_code: unicode
        """
        # Lets do magic and change site_id for this token (why even ebay allows it, do not ask me...)
        self.ebay_token.site_id = settings.EBAY_SUPPORTED_SITES[country_code]
        return self.ebay_token
