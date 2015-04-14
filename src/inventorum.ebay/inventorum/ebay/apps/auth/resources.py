# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db.transaction import atomic
from inventorum.ebay.apps.auth.serializers import AuthorizeEbayParametersSerializer
from inventorum.ebay.apps.auth.services import AuthorizationService
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.lib.rest.resources import UnauthorizedEbayAPIResource
from rest_framework.response import Response


class AuthorizeEbayResource(UnauthorizedEbayAPIResource):

    def get(self, request):
        ebay = EbayAuthentication()
        session_id = ebay.get_session_id()
        url = EbayAuthentication.get_url_from_session_id(session_id)

        return Response({
            'url': url,
            'session_id': session_id
        })

    @atomic
    def post(self, request):
        serializer = AuthorizeEbayParametersSerializer(data=request.DATA)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.data['session_id']
        service = AuthorizationService(request.user)
        service.assign_token_from_session_id(session_id)
        service.fetch_user_data_from_ebay()

        return Response()
