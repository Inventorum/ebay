# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db.transaction import atomic
from django.utils.translation import ugettext
from inventorum.ebay.apps.auth.serializers import AuthorizeEbayGetSerializer
from inventorum.ebay.apps.auth.services import AuthorizationService
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication
from inventorum.ebay.lib.rest.exceptions import BadRequest
from inventorum.ebay.lib.rest.resources import UnauthorizedEbayAPIResource
from rest_framework.response import Response


class AuthorizeEbayResource(UnauthorizedEbayAPIResource):
    SESSION_KEY_FOR_SESSION_ID = "ebay_auth_session_id"

    serializer_class = AuthorizeEbayGetSerializer

    def get(self, request):
        ebay = EbayAuthentication()
        session_id = ebay.get_session_id()
        url = EbayAuthentication.get_url_from_session_id(session_id)

        class AuthData(object):
            def __init__(self, url):
                self.url = url

        request.session[self.__class__.SESSION_KEY_FOR_SESSION_ID] = session_id
        serializer = self.get_serializer(AuthData(url))
        return Response(serializer.data)

    @atomic
    def post(self, request):
        session_id = request.session.get(self.__class__.SESSION_KEY_FOR_SESSION_ID, None)
        if not session_id:
            raise BadRequest(ugettext("You need to authenticate URL from GET request first!"),
                             key='ebay.auth.missing.session_id')
        service = AuthorizationService(request.user)
        service.assign_token_from_session_id(session_id)
        service.fetch_user_data_from_ebay()

        return Response()
