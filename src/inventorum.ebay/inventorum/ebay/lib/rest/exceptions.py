# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from rest_framework.exceptions import ValidationError
from rest_framework import status


class BadRequest(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'common.unknown'