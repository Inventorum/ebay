# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from rest_framework.permissions import BasePermission


class IsEbayAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated() and \
               request.user.account and request.user.account.token and \
               not request.user.account.token.is_expired