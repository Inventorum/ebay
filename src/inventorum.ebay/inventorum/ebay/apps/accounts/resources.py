# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer

from inventorum.ebay.lib.rest.resources import APIResource
from rest_framework import mixins


log = logging.getLogger(__name__)


class EbayAccountResource(APIResource, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    serializer_class = EbayAccountSerializer

    def get_object(self):
        return self.request.user.account

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
