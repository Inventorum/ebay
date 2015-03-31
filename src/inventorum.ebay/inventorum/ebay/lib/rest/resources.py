# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class UnauthorizedEbayAPIResource(APIView):
    permission_classes = (IsAuthenticated,)


class APIResource(UnauthorizedEbayAPIResource):
    permission_classes = UnauthorizedEbayAPIResource.permission_classes + ()  # we will have here in future new check
