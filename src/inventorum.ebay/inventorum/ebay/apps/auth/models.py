# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db.models.fields import DateTimeField
from django_extensions.db.fields.encrypted import EncryptedTextField
from inventorum.ebay.lib.db.models import BaseModel


class EbayTokenModel(BaseModel):
    value = EncryptedTextField()
    expiration_date = DateTimeField()

    @classmethod
    def create_from_ebay_token(cls, ebay_token):
        return cls.objects.create(
            value=ebay_token.value,
            expiration_date=ebay_token.expiration_time
        )
