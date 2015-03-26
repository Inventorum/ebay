# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class APIResource(APIView):
    permission_classes = (IsAuthenticated,)
