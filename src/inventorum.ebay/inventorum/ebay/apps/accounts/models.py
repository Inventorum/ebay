# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings

from django.db.models.fields import CharField, EmailField, BooleanField, DateTimeField, DecimalField, TextField, \
    URLField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django_countries.fields import CountryField

from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurable

from inventorum.ebay.lib.auth.models import AuthenticableModelMixin
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel, MappedInventorumModelQuerySet
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayLocation
from inventorum.util.django.model_utils import PassThroughManager


log = logging.getLogger(__name__)


class AddressModel(BaseModel):
    """ Represents an address model """
    name = CharField(max_length=255)
    # TODO jm: Rename to street1 and street2
    street = CharField(max_length=255, null=True, blank=True)
    street1 = CharField(max_length=255, null=True, blank=True)
    postal_code = CharField(max_length=255, null=True, blank=True)
    city = CharField(max_length=255, null=True, blank=True)
    region = CharField(max_length=255, null=True, blank=True)
    country = CountryField(null=True, blank=True)

    @property
    def first_name(self):
        return self._split_name()[0]

    @property
    def last_name(self):
        return self._split_name()[1]

    def _split_name(self):
        """
        Splits the `name` into first and last name
        :rtype: (unicode, unicode)
        """
        if " " in self.name:
            # split name on the *first* occurrence of " "
            return self.name.split(" ", 1)
        else:
            return self.name, ""

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

    def ebay_authenticated(self):
        """
        :rtype: EbayAccountModelQuerySet
        """
        return self.filter(token__isnull=False)

    def with_published_products(self):
        """
        :rtype: EbayAccountModelQuerySet
        """
        return self.filter(products__items__publishing_status=EbayItemPublishingStatus.PUBLISHED).distinct()


class EbayAccountModel(ShippingServiceConfigurable, MappedInventorumModel):
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

    last_core_products_sync = DateTimeField(null=True, blank=True)
    last_core_orders_sync = DateTimeField(null=True, blank=True)
    last_ebay_orders_sync = DateTimeField(null=True, blank=True)

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

    @property
    def is_ebay_authenticated(self):
        return self.token is not None

    @property
    def has_location(self):
        return hasattr(self, "location")


class EbayLocationModel(BaseModel):
    account = OneToOneField(EbayAccountModel, related_name="location", null=True, blank=True)
    address = ForeignKey(AddressModel, null=True, blank=True, related_name="locations",
                                      verbose_name="Registration address")
    latitude = DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    longitude = DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    name = CharField(max_length=255, null=True, blank=True)
    phone = CharField(max_length=255, null=True, blank=True)
    pickup_instruction = TextField(null=True, blank=True)
    url = URLField(null=True, blank=True)

    def get_ebay_location_object(self, days):
        """
        Days are comming from `core_account` thats why we need to pass them, so lets pass them as ebay object
        :type days: list[inventorum.ebay.lib.ebay.data.inventorymanagement.EbayDay]
        :rtype: EbayLocation
        """
        return EbayLocation(
            location_id=self.account.ebay_location_id,
            address1=self.address.street,
            address2=self.address.street1,
            city=self.address.city,
            country=self.address.country,
            days=days,
            latitude=self.latitude,
            longitude=self.longitude,
            name=self.name,
            phone=self.phone,
            pickup_instruction=self.pickup_instruction,
            postal_code=self.address.postal_code,
            region=self.address.region,
            url=self.url,
            utc_offset="+02:00"  # TODO: What to do with it???
            )


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
