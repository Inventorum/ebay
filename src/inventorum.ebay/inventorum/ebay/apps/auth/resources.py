# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db.transaction import atomic
from inventorum.ebay.apps.auth.serializers import AuthorizeEbayParametersSerializer, AuthorizeEbayGetSerializer
from inventorum.ebay.apps.auth.services import AuthorizationService, AuthorizationServiceException
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.lib.rest.exceptions import BadRequest
from inventorum.ebay.lib.rest.resources import UnauthorizedEbayAPIResource
from rest_framework.response import Response


class AuthorizeEbayResource(UnauthorizedEbayAPIResource):
    serializer_class = AuthorizeEbayGetSerializer

    def get(self, request):
        ebay = EbayAuthentication()
        session_id = ebay.get_session_id()
        url = EbayAuthentication.get_url_from_session_id(session_id)

        class AuthData(object):
            def __init__(self, url, session_id):
                self.url = url
                self.session_id = session_id

        serializer = self.get_serializer(AuthData(url, session_id))
        return Response(serializer.data)

    @atomic
    def post(self, request):
        serializer = AuthorizeEbayParametersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.data['session_id']
        service = AuthorizationService(request.user)
        try:
            service.assign_token_from_session_id(session_id)
            service.fetch_user_data_from_ebay()
        except AuthorizationServiceException as e:
            raise BadRequest(e.message, key="auth.service.error")

        return Response()
