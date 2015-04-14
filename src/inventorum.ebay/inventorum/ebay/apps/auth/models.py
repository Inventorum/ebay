# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from django.db.models.fields import DateTimeField
from django.db.models.query_utils import Q
from django_extensions.db.fields.encrypted import EncryptedTextField

from inventorum.ebay.lib.db.models import BaseModel, BaseQuerySet
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.util.django.model_utils import PassThroughManager


class EbayTokenModelQuerySet(BaseQuerySet):
    def __init__(self, *args, **kwargs):
        super(EbayTokenModelQuerySet, self).__init__(*args, **kwargs)
        self.query.add_q(Q(expiration_date__gt=timezone.now()))


class EbayTokenModel(BaseModel):
    value = EncryptedTextField()
    expiration_date = DateTimeField()

    objects = PassThroughManager.for_queryset_class(EbayTokenModelQuerySet)()

    @classmethod
    def create_from_ebay_token(cls, ebay_token):
        return cls.objects.create(
            value=ebay_token.value,
            expiration_date=ebay_token.expiration_time
        )

    @property
    def ebay_object(self):
        return EbayToken(self.value, self.expiration_date)

    @property
    def is_expired(self):
        return self.expiration_date <= timezone.now()