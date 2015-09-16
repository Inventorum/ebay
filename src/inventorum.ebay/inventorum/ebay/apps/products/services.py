# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict

import logging
from decimal import Decimal

from django.utils.functional import cached_property
from django.utils.translation import ugettext
from inventorum.ebay.apps.products.validators import CategorySpecificsValidator
from inventorum.ebay.lib.ebay.data import BuyerPaymentMethodCodeType, EbayConstants, SellerProfileCodeType
from inventorum.ebay.lib.ebay.data.errors import EbayErrorCode
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayLocationAvailability, EbayAvailability
from inventorum.ebay.lib.ebay.inventorymanagement import EbayInventoryManagement
from inventorum.ebay.lib.ebay.preferences import EbayPreferences
from inventorum.util.django.timezone import datetime
from requests.exceptions import RequestException

from inventorum.ebay.apps.products import EbayItemPublishingStatus, EbayApiAttemptType, EbayItemUpdateStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod, EbayItemSpecificModel, EbayApiAttempt, EbayItemVariationModel, \
    EbayItemVariationSpecificModel, EbayItemVariationSpecificValueModel
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


class EbayServiceException(Exception):

    def __init__(self, message=None, original_exception=None):
        super(Exception, self).__init__(message)
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


class PublishingCouldNotGetDataFromEbayException(EbayServiceException):
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
        """
        :rtype: inventorum.ebay.apps.core_api.models.CoreProduct
        """
        try:
            return self.user.core_api.get_product(self.product.inv_id)
        except RequestException as e:
            raise PublishingCouldNotGetDataFromCoreAPI(response=e.response)

    @cached_property
    def core_info(self):
        """
        :rtype: inventorum.ebay.apps.core_api.models.CoreInfo
        """
        try:
            return self.user.core_api.get_account_info()
        except RequestException as e:
            raise PublishingCouldNotGetDataFromCoreAPI(e.response)

    @cached_property
    def ebay_user_preferences(self):
        """
        :rtype: inventorum.ebay.lib.ebay.data.preferences.GetUserPreferencesResponseType
        """
        try:
            ebay_preferences = EbayPreferences(token=self.account.token.ebay_object)
            return ebay_preferences.get_user_preferences()
        except EbayConnectionException as e:
            raise PublishingCouldNotGetDataFromEbayException(e.response)

    def _get_default_return_policy_from_ebay(self):
        """
        :rtype: None | inventorum.ebay.lib.ebay.data.preferences.SupportedSellerProfileType
        :return:
        """
        user_preferences = self.ebay_user_preferences
        seller_profiles = user_preferences.seller_profile_preferences.supported_seller_profiles

        if not len(seller_profiles):
            return None

        # find and return the default return policy (there should be at most one) or None there was none
        return next((p for p in seller_profiles if p.profile_type == SellerProfileCodeType.RETURN_POLICY
                     and p.category_group.is_default), None)

    @property
    def core_account(self):
        """
        :rtype: inventorum.ebay.lib.core_api.models.CoreAccount
        """
        return self.core_info.account

    def validate(self):
        """
        Validates account and product before publishing to ebay
        :raises: PublishingValidationException
        """
        self._validate_product_existence_in_core_api()

        if self.product.is_published:
            raise PublishingValidationException(ugettext('Product is already published'))

        if self.product.is_being_published:
            raise PublishingValidationException(ugettext("Product is already being published"))

        if not self.core_account.billing_address:
            raise PublishingValidationException(ugettext('To publish product we need your billing address'))

        if not (self.product.shipping_services.exists() or self.account.shipping_services.exists()):
            raise PublishingValidationException(ugettext('Neither product or account have configured shipping services'))

        self._validate_prices()
        self._validate_attributes_in_variations()

        if not self.product.category_id:
            raise PublishingValidationException(ugettext('You need to select category'))

        self._validate_ean()
        self._validate_return_policy()

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

        if self.product.is_click_and_collect and self.core_account.settings.ebay_click_and_collect:
            # Click and collect valid here
            if BuyerPaymentMethodCodeType.PayPal not in self.account.ebay_payment_methods:
                raise PublishingValidationException(ugettext('Click&Collect requires to use PayPal as payment method!'))

        if BuyerPaymentMethodCodeType.PayPal in self.account.ebay_payment_methods and \
                not self.account.payment_method_paypal_email_address:
            raise PublishingValidationException(ugettext('Missing paypal email addres, however paypal payment method '
                                                         'is enabled!'))

    def _validate_product_existence_in_core_api(self):
        return self.core_product

    def _validate_prices(self):
        if not self.core_product.is_parent and self.core_product.gross_price < Decimal("1"):
            raise PublishingValidationException(ugettext('Price needs to be greater or equal than 1'))

        if self.core_product.is_parent and any([v.gross_price < Decimal("1") for v in self.core_product.variations]):
            raise PublishingValidationException(ugettext('Prices needs to be greater or equal than 1'))

    def _validate_attributes_in_variations(self):
        """
        Ensure that each variation has the same number of attributes and that each variation has at least one attribute.
        :return:
        """
        variations = self.core_product.variations
        if not variations:
            return

        specifics_in_variations = defaultdict(int)
        for variation in variations:
            for attribute in variation.attributes:
                specifics_in_variations[attribute.key] += len(attribute.values)

        max_attrs = len(variations)
        all_variations_has_the_same_attributes = all([a == max_attrs for a in specifics_in_variations.values()])

        if not specifics_in_variations:
            raise PublishingValidationException(ugettext("Variations need to have at least one attribute"))

        if not all_variations_has_the_same_attributes:
            raise PublishingValidationException(ugettext("All variations needs to have exactly the same number of "
                                                         "attributes"))

    def _validate_ean(self):
        """
        Since the GTIN mandate, some ebay categories require a valid EAN code for item.
        This method is responsible for validating the EAN for these categories. In case
        of variations, it validates whether each variation has a EAN.

        :raises: PublishingValidationException
        """
        if not self.product.category.features.ean_required or self.product.ean_does_not_apply:
            return

        # no variations => core product is expected to have EAN
        if not self.core_product.has_variations and not self.core_product.ean:
            raise PublishingValidationException(ugettext("The selected category requires a valid EAN"))
        # variations => every variation is expected to have EAN
        elif self.core_product.variations and not all(v.ean for v in self.core_product.variations):
            raise PublishingValidationException(
                ugettext("The selected category requires each variation to have a valid EAN"))

    def _validate_return_policy(self):
        """
        Validates whether the ebay account has a default return policy configured.
        For now, we publish every item with the default return policy configured on the eBay website.
        If there is none, we disallow the publishing for legal matters.

        :raises: PublishingValidationException
        """
        default_return_policy = self._get_default_return_policy_from_ebay()
        if default_return_policy is None:
            raise PublishingValidationException(ugettext('Product could not be published! There is no default '
                                                         'return policy defined in your eBay account.'))

    def create_ebay_item(self):
        """
        :rtype: EbayItemModel
        """
        # We should think about adding tax_rate to the product details response :-)
        tax_rate = self.core_info.get_tax_rate_for(self.core_product.tax_type_id)
        if tax_rate is None:
            raise PublishingException(message="Cannot determine tax_rate for core_product.tax_type={}"
                                      .format(self.core_product.tax_type_id))

        # ean applies unless product has and cannot have a ean, e.g. when they are self-made
        ean_applies = not self.product.ean_does_not_apply

        if ean_applies and not self.core_product.has_variations:
            ean = self.core_product.ean
        elif not self.core_product.has_variations:
            ean = EbayConstants.ProductIdentifierUnavailableText
        else:
            ean = None

        return_policy = self._get_default_return_policy_from_ebay()

        item = EbayItemModel.objects.create(
            product=self.product,
            inv_product_id=self.core_product.id,
            account=self.product.account,
            name=self.core_product.name,
            ean=ean,
            description=self.core_product.description,
            gross_price=self.core_product.gross_price,
            tax_rate=tax_rate,
            category=self.product.category,
            country=self.core_account.country,
            quantity=self.core_product.quantity,
            listing_duration=self.product.category.features.max_listing_duration,
            paypal_email_address=self.account.payment_method_paypal_email_address,
            postal_code=self.core_account.billing_address.zipcode,
            is_click_and_collect=self.product.is_click_and_collect,
            ebay_seller_profile_return_policy_id=return_policy.profile_id
        )

        for image in self.core_product.images:
            EbayItemImageModel.objects.create(
                inv_image_id=image.id,
                url=image.urls.ipad_retina,
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

        for payment in self.account.ebay_payment_methods:
            EbayItemPaymentMethod.objects.create(
                external_id=payment,
                item=item
            )

        for specific in self.product.specific_values.all():
            EbayItemSpecificModel.objects.create(
                specific=specific.specific,
                value=specific.value,
                item=item
            )

        for variation in self.core_product.variations:
            tax_rate = self.core_info.get_tax_rate_for(variation.tax_type_id)
            if tax_rate is None:
                raise PublishingException(message="Cannot determine tax_rate for variation with variation.tax_type={}"
                                          .format(variation.tax_type_id))
            variation_obj = EbayItemVariationModel.objects.create(
                inv_product_id=variation.id,
                ean=variation.ean if ean_applies else EbayConstants.ProductIdentifierUnavailableText,
                quantity=variation.quantity,
                gross_price=variation.gross_price,
                tax_rate=tax_rate,
                item=item
            )

            for image in variation.images:
                EbayItemImageModel.objects.create(
                    inv_image_id=image.id,
                    url=image.urls.ipad_retina,
                    variation=variation_obj
                )

            for attribute in variation.attributes:
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
        self.item = item
        self.user = user

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
                self.user.core_api.post_product_publishing_state(self.item.inv_product_id, core_api_state, details=details)
            except RequestException as e:
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
        self._add_inventory_for_click_and_collect()

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

        details = None
        if response.message:
            details = {'message': response.message}

        self.item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, details=details, save=False)
        self.item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=ebay_api,
            item=self.item,
            type=EbayApiAttemptType.PUBLISH
        )

    def _add_inventory_for_click_and_collect(self):
        if not self.item.is_click_and_collect:
            return

        api = EbayInventoryManagement(token=self.user.account.token.ebay_object)

        locations_availability = [
            EbayLocationAvailability(
                availability=EbayAvailability.IN_STOCK,
                location_id=self.user.account.ebay_location_id,
                quantity=None
            )
        ]
        api.add_inventory(self.item.sku, locations_availability=locations_availability)

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

        response = None
        try:
            response = service.unpublish(self.item.external_id)
        except EbayConnectionException as e:
            self.item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, details=e.serialized_errors)
            has_error_that_item_was_already_unpublished = \
                any([err.code == EbayErrorCode.TheAuctionHasBeenClosed for err in e.errors])
            if not has_error_that_item_was_already_unpublished:
                EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                    exception=e,
                    item=self.item,
                    type=EbayApiAttemptType.UNPUBLISH
                )

                raise UnpublishingException(e.message, original_exception=e)

        self._delete_inventory_for_click_and_collect()

        if response:
            self.item.unpublished_at = response.end_time
        else:
            self.item.unpublished_at = datetime.now()

        self.item.set_publishing_status(EbayItemPublishingStatus.UNPUBLISHED, save=False)
        self.item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=service,
            item=self.item,
            type=EbayApiAttemptType.UNPUBLISH
        )

    def _delete_inventory_for_click_and_collect(self):
        if not self.item.is_click_and_collect:
            return

        api = EbayInventoryManagement(token=self.user.account.token.ebay_object)
        try:
            api.delete_inventory(self.item.sku, delete_all=True)
        except EbayConnectionException as e:
            log.exception('Got exception when removing inventory from C&C, item id: %s', self.item.pk)

    def finalize_unpublish_attempt(self):
        """
        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(self.item.publishing_status,
                                                details=self.item.publishing_status_details)


class CorePublishingStatusUpdateService(object):
    """
    Responsible for updating the core publishing status for a product based on the given source item
    """

    def __init__(self, source, account):
        """
        :type source: EbayItemModel
        :type account: EbayAccountModel
        """
        self.ebay_item = source
        self.product = source.product
        self.account = account

    def update_publishing_status(self):
        """
        Updates the core publishing status for the corresponding product based on the given source item

        :raises requests.exceptions.RequestException
        """
        publishing_status = self.ebay_item.publishing_status
        details = self.ebay_item.publishing_status_details

        log.info("Updating publishing status for product {product} to '{status}' {details}"
                 .format(product=self.product, status=publishing_status,
                         details="({})".format(details) if details else ""))

        core_api_state = EbayItemPublishingStatus.core_api_state(publishing_status)
        self.account.core_api.post_product_publishing_state(self.ebay_item.inv_product_id, core_api_state, details=details)


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
