# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class AuthorizeEbayParametersSerializer(Serializer):
    session_id = CharField()