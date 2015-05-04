# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.models import EbayLocationModel
from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer
from inventorum.ebay.apps.accounts.services import EbayLocationUpdateService, EbayLocationUpdateServiceException
from inventorum.ebay.lib.rest.exceptions import BadRequest

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
        response = self.update(request, *args, **kwargs)

        # self.update will perform save on database objects so we can do update to ebay now
        service = EbayLocationUpdateService(request.user)
        if not service.can_be_saved:
            return response

        try:
            service.update()
        except EbayLocationUpdateServiceException as e:
            raise BadRequest(e.message, key='ebay.api.error')

        return response
