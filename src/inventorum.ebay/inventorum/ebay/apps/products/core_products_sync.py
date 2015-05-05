# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime
from inventorum.ebay.apps.products import tasks, EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemUpdateModel, \
    EbayItemVariationModel, EbayItemVariationUpdateModel
from inventorum.util.celery import TaskExecutionContext


log = logging.getLogger(__name__)


class CoreProductsSync(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        self.item_update_for_variations = {}

    def run(self):
        current_sync_start = datetime.utcnow()
        # if there was no sync yet, the ebay account creation is taken as starting point
        last_sync_start = self.account.last_core_products_sync or self.account.time_added

        self._sync_core_modifications(modified_since=last_sync_start)
        self._sync_core_deletions(deleted_since=last_sync_start)
        self._sync_variations_modifications()

        self.account.last_core_products_sync = current_sync_start
        self.account.save()

    def _sync_core_modifications(self, modified_since):
        """
        :type modified_since: datetime
        """
        modifications_of_published_items = \
            self._get_core_modifications_of_published_items(modified_since=modified_since)

        for ebay_item_or_variation, core_product_delta in modifications_of_published_items:
            if isinstance(ebay_item_or_variation, EbayItemModel):
                self._sync_ebay_item(ebay_item_or_variation, core_product_delta)
            elif isinstance(ebay_item_or_variation, EbayItemVariationModel):
                self._sync_ebay_variation(ebay_item_or_variation, core_product_delta)

    def _sync_ebay_item(self, ebay_item, core_product_delta):
        ebay_item_update = self._create_item_update_from_diff(ebay_item, core_product_delta)
        if ebay_item_update:
            tasks.schedule_ebay_item_update(ebay_item_update.id, context=self.get_task_execution_context())

    def _sync_ebay_variation(self, ebay_variation, core_product_delta):
        self._create_variation_update_from_diff(ebay_variation, core_product_delta)

    def _create_update_kwargs_from_diff(self, object, core_product_delta):
        """
        :type object: inventorum.ebay.apps.products.models.EbayUpdateModel
        :param core_product_delta: inventorum.ebay.apps.core_api.models.CoreProductDelta
        :rtype: dict
        """
        updated_attributes = {}
        if object.gross_price != core_product_delta.gross_price:
            updated_attributes["gross_price"] = core_product_delta.gross_price

        if object.quantity != core_product_delta.quantity:
            updated_attributes["quantity"] = core_product_delta.quantity

        return updated_attributes

    def _create_variation_update_from_diff(self, ebay_variation, core_product_delta):
        """
        :type ebay_variation: EbayItemVariationModel
        :type core_product_delta: inventorum.ebay.apps.core_api.models.CoreProductDelta

        :rtype: EbayItemVariationUpdateModel | None
        """
        updated_attributes = self._create_update_kwargs_from_diff(ebay_variation, core_product_delta)
        if updated_attributes:
            update_item = self._get_update_item_for_variation(ebay_variation)
            return EbayItemVariationUpdateModel.objects.create(variation=ebay_variation,
                                                               update_item=update_item,
                                                               **updated_attributes)

        return None

    def _get_update_item_for_variation(self, ebay_variation):
        """
        :type ebay_variation: EbayItemVariationModel
        :rtype: EbayItemUpdateModel
        """
        if not self.item_update_for_variations.get(ebay_variation.item.pk, None):
            self.item_update_for_variations[ebay_variation.item.pk] = \
                EbayItemUpdateModel.objects.create(item=ebay_variation.item)
        return self.item_update_for_variations[ebay_variation.item.pk]

    def _create_item_update_from_diff(self, ebay_item, core_product_delta):
        """
        :type ebay_item: EbayItemModel
        :type core_product_delta: inventorum.ebay.apps.core_api.models.CoreProductDelta

        :rtype: EbayItemUpdateModel | None
        """
        updated_attributes = self._create_update_kwargs_from_diff(ebay_item, core_product_delta)
        if updated_attributes:
            return EbayItemUpdateModel.objects.create(item=ebay_item, **updated_attributes)

        return None

    def get_task_execution_context(self):
        return TaskExecutionContext(user_id=self.account.default_user.id,
                                    account_id=self.account.id,
                                    request_id=None)

    def _sync_core_deletions(self, deleted_since):
        """
        :type deleted_since: datetime
        """
        deletions_ids = self._get_deletions_ids_of_ebay_products(deleted_since=deleted_since)

        for ebay_product in EbayProductModel.objects.by_account(self.account).filter(inv_id__in=deletions_ids):
            ebay_product.deleted_in_core_api = True
            ebay_product.save()

            tasks.schedule_ebay_product_deletion(ebay_product.id, context=self.get_task_execution_context())

        deleted_variations = EbayItemVariationModel.objects.filter(inv_product_id__in=deletions_ids)
        for deleted_variation in deleted_variations:
            item = self._get_update_item_for_variation(deleted_variation)
            EbayItemVariationUpdateModel.objects.create(variation=deleted_variation, update_item=item, is_deleted=True)

    def _get_core_modifications_of_published_items(self, modified_since):
        """
        Returns product deltas of products that are published to ebay and have been modified since the given datetime

        :type modified_since: datetime
        :rtype: collections.Iterable[(EbayItemModel | EbayItemVariationModel, inventorum.ebay.apps.core_api.models.CoreProductDelta)]
        """

        delta_pages = self.account.core_api.get_paginated_product_delta_modified(start_date=modified_since)
        for page in delta_pages:
            for core_product_delta in page:
                published_item = self._get_item_or_variation(core_product_delta)

                if not published_item:
                    continue

                yield published_item, core_product_delta

    def _get_item_or_variation(self, core_product_delta):
        published_core_product_ids = EbayProductModel.objects.published().by_account(self.account)\
            .values_list("inv_id", flat=True)
        is_published = lambda core_product_id: core_product_id in published_core_product_ids

        main_product_id = core_product_delta.parent or core_product_delta.id
        if not is_published(main_product_id):
            return None

        published_item = EbayItemModel.objects.get(publishing_status=EbayItemPublishingStatus.PUBLISHED,
                                                   product__inv_id=main_product_id)

        if published_item.has_variations:
            return published_item.variations.get(inv_product_id=core_product_delta.id)

        return published_item

    def _get_deletions_ids_of_ebay_products(self, deleted_since):
        """
        Returns the mapped ebay products of core products that have been deleted since the given datetime

        :type deleted_since: datetime
        :rtype: collections.Iterable[EbayProductModel]
        """
        deleted_core_product_ids = list()

        deleted_ids_pages = self.account.core_api.get_paginated_product_delta_deleted(start_date=deleted_since)

        for deleted_ids in deleted_ids_pages:
            deleted_core_product_ids += deleted_ids

        return deleted_core_product_ids

    def _sync_variations_modifications(self):
        if not self.item_update_for_variations:
            return

        for item_update in self.item_update_for_variations.values():
            tasks.schedule_ebay_item_update(item_update.id, context=self.get_task_execution_context())
