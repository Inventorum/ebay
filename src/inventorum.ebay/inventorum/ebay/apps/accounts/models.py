# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings
from django.db.models.fields import CharField, EmailField, BooleanField, DateTimeField
from django.db.models.fields.related import ForeignKey
from django_countries.fields import CountryField

from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.apps.products import EbayItemPublishingStatus

from inventorum.ebay.lib.auth.models import AuthenticableModelMixin
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel, MappedInventorumModelQuerySet
from inventorum.util.django.model_utils import PassThroughManager


log = logging.getLogger(__name__)


class AddressModel(BaseModel):
    """ Represents an address model """
    name = CharField(max_length=255)
    street = CharField(max_length=255, null=True, blank=True)
    street1 = CharField(max_length=255, null=True, blank=True)
    city = CharField(max_length=255, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    postal_code = CharField(max_length=255, null=True, blank=True)

    @classmethod
    def create_from_ebay_address(cls, ebay_address):
        """

        :param ebay_address:
        :return:

        :type ebay_address: inventorum.ebay.lib.ebay.data.EbayUserAddress
        """
        return cls.objects.create(
            name=ebay_address.name,
            street=ebay_address.street,
            street1=ebay_address.street1,
            city=ebay_address.city,
            country=ebay_address.country,
            postal_code=ebay_address.postal_code
        )


class EbayAccountModelQuerySet(MappedInventorumModelQuerySet):

    def with_published_products(self):
        """
        :rtype: EbayProductModelQuerySet
        """
        return self.filter(products__items__publishing_status=EbayItemPublishingStatus.PUBLISHED).distinct()


class EbayAccountModel(MappedInventorumModel):
    """ Represents an inventorum account in the ebay context """
    token = ForeignKey("auth.EbayTokenModel", null=True, blank=True, related_name="accounts",
                       verbose_name="Ebay token")
    registration_address = ForeignKey(AddressModel, null=True, blank=True, related_name="accounts",
                                      verbose_name="Registration address")
    email = EmailField(null=True, blank=True)
    id_verified = BooleanField(default=False)
    store_owner = BooleanField(default=False)
    qualifies_for_b2b_vat = BooleanField(default=False)
    status = CharField(max_length=255, null=True, blank=True)
    user_id = CharField(max_length=255, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    registration_date = DateTimeField(null=True, blank=True)
    ebay_location_uuid = CharField(max_length=36, null=True, blank=True)

    last_core_api_sync = DateTimeField(null=True, blank=True)

    objects = PassThroughManager.for_queryset_class(EbayAccountModelQuerySet)()

    @property
    def ebay_location_id(self):
        return settings.EBAY_LOCATION_ID_FORMAT.format(self.inv_id)

    @property
    def default_user(self):
        """
        :rtype: EbayUserModel
        """
        return self.users.first()

    @property
    def core_api(self):
        """
        :rtype: UserScopedCoreAPIClient
        """
        return self.default_user.core_api


class EbayUserModel(MappedInventorumModel, AuthenticableModelMixin):
    """ Represents an inventorum user in the ebay context """
    account = ForeignKey(EbayAccountModel, related_name="users", verbose_name="Account")

    @property
    def core_api(self):
        """
        :return: User-scoped core api client
        :rtype: UserScopedCoreAPIClient
        """
        return UserScopedCoreAPIClient(user_id=self.inv_id, account_id=self.account.inv_id)
