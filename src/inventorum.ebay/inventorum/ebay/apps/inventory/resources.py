# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.translation import ugettext

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status

from inventorum.ebay.lib.rest.exceptions import ApiException, BadRequest

from inventorum.ebay.lib.rest.resources import APIResource


log = logging.getLogger(__name__)



class SanityCheckResource(APIResource):
    def post(self, request):
        log.info(request.data)
        return Response(data={})