# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.rest.resources import APIResource
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


log = logging.getLogger(__name__)


class PublishResource(APIResource):

    def post(self, request, pk):
        return Response()
