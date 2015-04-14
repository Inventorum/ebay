# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    def build_error_data(detail, key):
        return {
            'detail': detail,
            'key': key
        }

    response = exception_handler(exc, context)
    if response and response.data and 'detail' in response.data:
        exc_name = exc.__class__.__name__
        response.data['error'] = build_error_data(response.data['detail'],
                                                  'rest_framework.internal.{exc_name}'.format(exc_name=exc_name))
    if response is None and isinstance(exc, ApiException):
        response = Response(data={
            'error': build_error_data(exc.detail, exc.key)
        }, status=exc.status_code)

    return response


ValidationError.key = 'validation.failed'


class ApiException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail, key="common.unknown", status_code=None):
        # For validation errors the 'detail' key is always required.
        # The details should always be coerced to a list if not already.
        self.detail = detail
        self.key = key
        if status_code is not None:
            self.status_code = status_code


class BadRequest(ApiException):
    status_code = status.HTTP_400_BAD_REQUEST


class NotFound(ApiException):
    status_code = status.HTTP_404_NOT_FOUND
