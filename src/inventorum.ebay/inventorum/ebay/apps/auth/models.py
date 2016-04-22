# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from django.conf import settings
from django.db.models.fields import DateTimeField, IntegerField
from django.db.models.query_utils import Q
from django_extensions.db.fields.encrypted import EncryptedTextField

from inventorum.ebay.lib.db.models import BaseModel, BaseQuerySet
from inventorum.ebay.lib.ebay.data.authorization import EbayToken


class EbayTokenModelQuerySet(BaseQuerySet):
    def __init__(self, *args, **kwargs):
        super(EbayTokenModelQuerySet, self).__init__(*args, **kwargs)
        self.query.add_q(Q(expiration_date__gt=timezone.now()))


class EbayTokenModel(BaseModel):
    DEFAULT_SITE_ID = settings.EBAY_SUPPORTED_SITES['DE']

    value = EncryptedTextField()
    expiration_date = DateTimeField()
    site_id = IntegerField(default=DEFAULT_SITE_ID)  # default: DE

    objects = EbayTokenModelQuerySet.as_manager()

    @classmethod
    def create_from_ebay_token(cls, ebay_token):
        return cls.objects.create(
            value=ebay_token.value,
            expiration_date=ebay_token.expiration_time,
            site_id=ebay_token.site_id
        )

    @property
    def ebay_object(self):
        return EbayToken(self.value, self.expiration_date, site_id=self.site_id)

    @property
    def is_expired(self):
        return self.expiration_date <= timezone.now()
