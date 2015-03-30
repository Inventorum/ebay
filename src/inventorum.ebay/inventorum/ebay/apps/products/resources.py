# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.rest.resources import APIResource
from rest_framework.response import Response


log = logging.getLogger(__name__)


class PublishResource(APIResource):

    def post(self, request, inv_product_id):
        return Response()
