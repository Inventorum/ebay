# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import datetime
from django.utils.datetime_safe import datetime
from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.products import EbayProductPublishingStatus, tasks
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemUpdateModel


log = logging.getLogger(__name__)


def core_api_sync():
    accounts = EbayAccountModel.objects.with_published_products().all()
    for account in accounts:
        CoreAPISyncService(account).run()


class CoreAPISyncService(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def run(self):
        current_sync_start = datetime.now()
        # if there was no sync yet, the ebay account creation is taken as starting point
        last_sync_start = self.account.last_core_api_sync or self.account.time_added

        self._sync_core_modifications(modified_since=last_sync_start)
        self._sync_core_deletions(deleted_since=last_sync_start)

        self.account.last_core_api_sync = current_sync_start
        self.account.save()

    def _sync_core_modifications(self, modified_since):
        """
        :type modified_since: datetime
        """
        modifications_of_published_items = \
            self._get_core_modifications_of_published_items(modified_since=modified_since)

        for ebay_item, core_product_delta in modifications_of_published_items:
            if core_product_delta.quantity == 0:
                tasks.schedule_ebay_item_unpublish(ebay_item)
            else:
                ebay_item_update = self._create_update_from_diff(ebay_item, core_product_delta)
                if ebay_item_update:
                    tasks.schedule_ebay_item_update(ebay_item_update)

    def _create_update_from_diff(self, ebay_item, core_product_delta):
        """
        :type ebay_item: EbayItemModel
        :type core_product_delta: inventorum.ebay.apps.core_api.models.CoreProductDelta

        :rtype: EbayItemUpdateModel | None
        """
        updated_attributes = {}
        if ebay_item.gross_price != core_product_delta.gross_price:
            updated_attributes["gross_price"] = core_product_delta.gross_price

        if ebay_item.quantity != core_product_delta.quantity:
            updated_attributes["quantity"] = core_product_delta.quantity

        if updated_attributes:
            return EbayItemUpdateModel.objects.create(item=ebay_item, **updated_attributes)

        return None

    def _sync_core_deletions(self, deleted_since):
        """
        :type deleted_since: datetime
        """
        deletions = self._get_core_deletions_of_ebay_products(deleted_since=deleted_since)
        for ebay_product in deletions:
            ebay_product.deleted_in_core_api = True
            ebay_product.save()

            tasks.schedule_product_delete(ebay_product)

    def _get_core_modifications_of_published_items(self, modified_since):
        """
        Returns product deltas of products that are published to ebay and have been modified since the given datetime

        :type modified_since: datetime
        :rtype: collections.Iterable[(EbayItemModel, inventorum.ebay.apps.core_api.models.CoreProductDelta)]
        """
        published_core_product_ids = EbayProductModel.objects.published().values_list("inv_id", flat=True)
        is_published = lambda core_product_id: core_product_id in published_core_product_ids

        delta_pages = self.account.core_api.get_paginated_product_delta_modified(start_date=modified_since)
        for page in delta_pages:
            for core_product_delta in page:
                product_id = core_product_delta.id
                if is_published(product_id):
                    published_item = EbayItemModel.objects.get(publishing_status=EbayProductPublishingStatus.PUBLISHED,
                                                               product__inv_id=product_id)
                    yield published_item, core_product_delta

    def _get_core_deletions_of_ebay_products(self, deleted_since):
        """
        Returns the mapped ebay products of core products that have been deleted since the given datetime

        :type deleted_since: datetime
        :rtype: collections.Iterable[EbayProductModel]
        """
        deleted_core_product_ids = list()

        deleted_ids_pages = self.account.core_api.get_paginated_product_delta_deleted(start_date=deleted_since)

        for deleted_ids in deleted_ids_pages:
            deleted_core_product_ids.append(deleted_ids)

        for deleted_ebay_product in EbayProductModel.objects.filter(inv_id__in=deleted_core_product_ids):
            yield deleted_ebay_product
