# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict

import logging
from decimal import Decimal

from django.utils.functional import cached_property
from django.utils.translation import ugettext
from inventorum.ebay.apps.products.validators import CategorySpecificsValidator
from requests.exceptions import HTTPError

from inventorum.ebay.apps.products import EbayItemPublishingStatus, EbayApiAttemptType, EbayItemUpdateStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod, EbayItemSpecificModel, EbayApiAttempt, EbayItemVariationModel, \
    EbayItemVariationSpecificModel, EbayItemVariationSpecificValueModel
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


class EbayServiceException(Exception):
    def __init__(self, message=None, original_exception=None):
        self.message = message
        self.original_exception = original_exception


class PublishingException(EbayServiceException):
    pass


class UnpublishingException(EbayServiceException):
    pass


class PublishingValidationException(EbayServiceException):
    pass


class PublishingNotPossibleException(EbayServiceException):
    pass


class PublishingSendStateFailedException(EbayServiceException):
    pass


class PublishingCouldNotGetDataFromCoreAPI(EbayServiceException):
    def __init__(self, response):
        self.response = response


class PublishingPreparationService(object):
    def __init__(self, product, user):
        """
        :type product: EbayProductModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.product = product
        self.account = user.account
        self.user = user

    @cached_property
    def core_product(self):
        try:
            return self.user.core_api.get_product(self.product.inv_id)
        except HTTPError as e:
            raise PublishingCouldNotGetDataFromCoreAPI(response=e.response)

    @cached_property
    def core_info(self):
        try:
            return self.user.core_api.get_account_info()
        except HTTPError as e:
            raise PublishingCouldNotGetDataFromCoreAPI(e.response)

    @property
    def core_account(self):
        return self.core_info.account

    def validate(self):
        """
        Validates account and product before publishing to ebay
        :raises: PublishingValidationException
        """
        self._validate_product_existence_in_core_api()

        if self.product.is_published:
            raise PublishingValidationException(ugettext('Product was already published'))

        if not self.core_account.billing_address:
            raise PublishingValidationException(ugettext('To publish product we need your billing address'))

        if not (self.product.shipping_services.exists() or self.account.shipping_services.exists()):
            raise PublishingValidationException(ugettext('Neither product or account have configured shipping services'))

        self._validate_prices()
        self._validate_attributes_in_variations()

        if not self.product.category_id:
            raise PublishingValidationException(ugettext('You need to select category'))

        specific_values_ids = set(sv.specific.pk for sv in self.product.specific_values.all())
        required_ones = set(self.product.category.specifics.required().values_list('id', flat=True))

        missing_ids = (required_ones - specific_values_ids)
        if missing_ids:
            raise PublishingValidationException(
                ugettext('You need to pass all required specifics (missing: %(missing_ids)s)!')
                % {'missing_ids': list(missing_ids)})

        validator = CategorySpecificsValidator(category=self.product.category,
                                               specifics=[sv.specific for sv in self.product.specific_values.all()])
        validator.validate(raise_exception=False)
        if validator.errors:
            raise PublishingValidationException("\n".join(validator.errors))

        if self.product.is_click_and_collect and not self.core_account.settings.ebay_click_and_collect:
            raise PublishingValidationException(ugettext("You cannot publish product with Click & Collect, because you "
                                                         "don't have it enabled for your account!"))

    def _validate_product_existence_in_core_api(self):
        return self.core_product

    def _validate_prices(self):
        if not self.core_product.is_parent and self.core_product.gross_price < Decimal("1"):
            raise PublishingValidationException(ugettext('Price needs to be greater or equal than 1'))

        if self.core_product.is_parent and any([v.gross_price < Decimal("1") for v in self.core_product.variations]):
            raise PublishingValidationException(ugettext('Prices needs to be greater or equal than 1'))

    def _validate_attributes_in_variations(self):
        variations = self.core_product.variations
        if not variations:
            return

        specifics_in_variations = defaultdict(int)
        for variation in variations:
            for attribute in variation.attributes:
                specifics_in_variations[attribute.key] += len(attribute.values)

        max_attrs = max(specifics_in_variations.values())
        all_variations_has_the_same_attributes = all([a == max_attrs for a in specifics_in_variations.values()])
        if not all_variations_has_the_same_attributes:
            raise PublishingValidationException(ugettext("All variations needs to have exactly the same number of "
                                                         "attributes"))

    def create_ebay_item(self):
        """
        :rtype: EbayItemModel
        """
        product = EbayProductModel.objects.get(inv_id=self.core_product.id)

        item = EbayItemModel.objects.create(
            listing_duration=product.category.features.max_listing_duration,
            product=product,
            account=product.account,
            name=self.core_product.name,
            description=self.core_product.description,
            gross_price=self.core_product.gross_price,
            category=product.category,
            country=self.core_account.country,
            quantity=self.core_product.quantity,
            paypal_email_address=self.core_account.settings.ebay_paypal_email,
            postal_code=self.core_account.billing_address.zipcode,
            is_click_and_collect=self.product.is_click_and_collect
        )

        for image in self.core_product.images:
            EbayItemImageModel.objects.create(
                inv_id=image.id,
                url=image.url,
                item=item
            )

        shipping_services = self.product.shipping_services.all() if self.product.shipping_services.exists() \
            else self.account.shipping_services.all()

        for service_config in shipping_services:
            EbayItemShippingDetails.objects.create(
                additional_cost=service_config.additional_cost,
                cost=service_config.cost,
                external_id=service_config.service.external_id,
                item=item
            )

        for payment in self.core_account.settings.ebay_payment_methods:
            EbayItemPaymentMethod.objects.create(
                external_id=payment,
                item=item
            )

        for specific in product.specific_values.all():
            EbayItemSpecificModel.objects.create(
                specific=specific.specific,
                value=specific.value,
                item=item
            )

        for product in self.core_product.variations:
            variation_obj = EbayItemVariationModel.objects.create(
                quantity=product.quantity,
                gross_price=product.gross_price,
                item=item,
                inv_id=product.id
            )
            for image in product.images:
                EbayItemImageModel.objects.create(
                    inv_id=image.id,
                    url=image.url,
                    variation=variation_obj
                )
            for attribute in product.attributes:
                specific_obj = EbayItemVariationSpecificModel.objects.create(
                    name=attribute.key,
                    variation=variation_obj
                )
                for value in attribute.values:
                    EbayItemVariationSpecificValueModel.objects.create(
                        specific=specific_obj,
                        value=value
                    )

        return item


class PublishingUnpublishingService(object):
    def __init__(self, item, user):
        """
        Abstract base service for publishing/unpublishing products to ebay
        :type item: EbayItemModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.user = user
        self.item = item

    @property
    def product(self):
        return self.item.product

    def send_publishing_status_to_core_api(self, publishing_status, details=None):
        """
        :param publishing_status: see `EbayItemPublishingStatus`
        :type publishing_status: unicode
        :param details: Additional details, must be json serializable
        """
        core_api_state = EbayItemPublishingStatus.core_api_state(publishing_status)
        if core_api_state is not None:
            try:
                self.user.core_api.post_product_publishing_state(self.product.inv_id, core_api_state, details=details)
            except HTTPError as e:
                log.error(e)
                raise PublishingSendStateFailedException()
        else:
            log.warn('Got state (%s) that cannot be mapped to core api PublishState', publishing_status)


class PublishingService(PublishingUnpublishingService):
    def initialize_publish_attempt(self):
        """
        :raises PublishingSendStateFailedException
        """
        in_progress = EbayItemPublishingStatus.IN_PROGRESS
        self.send_publishing_status_to_core_api(publishing_status=in_progress)
        self.item.set_publishing_status(publishing_status=in_progress)

    def publish(self):
        """
        :raises PublishingException
        """
        ebay_api = EbayItems(self.user.account.token.ebay_object)
        try:
            response = ebay_api.publish(self.item.ebay_object)
        except EbayConnectionException as e:
            self.item.set_publishing_status(EbayItemPublishingStatus.FAILED, details=e.serialized_errors)

            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=self.item,
                type=EbayApiAttemptType.PUBLISH
            )

            raise PublishingException(e.message, original_exception=e)

        self.item.external_id = response.item_id
        self.item.published_at = response.start_time
        self.item.ends_at = response.end_time
        self.item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, save=False)
        self.item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=ebay_api,
            item=self.item,
            type=EbayApiAttemptType.PUBLISH
        )

    def finalize_publish_attempt(self):
        """
        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(self.item.publishing_status,
                                                details=self.item.publishing_status_details)


class UnpublishingService(PublishingUnpublishingService):
    def initialize_unpublish_attempt(self):
        """
        :raises PublishingSendStateFailedException
        """
        in_progress = EbayItemPublishingStatus.IN_PROGRESS
        self.send_publishing_status_to_core_api(publishing_status=in_progress)
        self.item.set_publishing_status(publishing_status=in_progress)

    def unpublish(self):
        """
        :raises UnpublishingException
        """
        service = EbayItems(self.user.account.token.ebay_object)
        try:
            response = service.unpublish(self.item.external_id)
        except EbayConnectionException as e:
            self.item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, details=e.serialized_errors)

            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=self.item,
                type=EbayApiAttemptType.UNPUBLISH
            )

            raise UnpublishingException(e.message, original_exception=e)

        self.item.unpublished_at = response.end_time
        self.item.set_publishing_status(EbayItemPublishingStatus.UNPUBLISHED, save=False)
        self.item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=service,
            item=self.item,
            type=EbayApiAttemptType.UNPUBLISH
        )

    def finalize_unpublish_attempt(self):
        """
        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(self.item.publishing_status,
                                                details=self.item.publishing_status_details)


class UpdateFailedException(EbayServiceException):
    pass


class UpdateService(object):
    def __init__(self, item_update, user):
        """
        :type item_update: inventorum.ebay.apps.products.models.EbayItemUpdateModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.user = user
        self.item_update = item_update

    def update(self):
        self.item_update.status = EbayItemUpdateStatus.IN_PROGRESS

        ebay_api = EbayItems(self.user.account.token.ebay_object)

        try:
            response = ebay_api.revise_fixed_price_item(self.item_update.ebay_object)
        except EbayConnectionException as e:
            self.item_update.set_status(EbayItemUpdateStatus.FAILED, details=e.serialized_errors)
            EbayApiAttempt.create_failed_update_attempt(self.item_update, exception=e)

            raise UpdateFailedException(e.message, original_exception=e)

        self.item_update.set_status(EbayItemUpdateStatus.SUCCEEDED)
        self._update_ebay_item_model()

        EbayApiAttempt.create_succeeded_update_attempt(item_update=self.item_update, ebay=ebay_api)

    def _update_ebay_item_model(self):
        """ Updates the item model after the update has been acked by ebay """
        ebay_item = self.item_update.item

        if not self.item_update.has_variation_updates:
            self._update_ebay_item_from_update_model(self.item_update, ebay_item)
        else:
            for update_variation in self.item_update.variations.all():
                variation = update_variation.variation
                self._update_ebay_item_from_update_model(update_variation, variation)

    def _update_ebay_item_from_update_model(self, update_model, model):
        if update_model.has_updated_quantity:
            model.quantity = update_model.quantity

        if update_model.has_updated_gross_price:
            model.gross_price = update_model.gross_price

        model.save()

class ProductDeletionService(object):
    def __init__(self, product, user):
        """
        :type product: EbayProductModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.product = product
        self.user = user

    def delete(self):
        """
        :raises UnpublishingException
        :rtype: bool
        """
        if self.product.is_published:
            ebay_item = self.product.published_item

            service = UnpublishingService(ebay_item, self.user)
            service.unpublish()

        self.product.delete()
