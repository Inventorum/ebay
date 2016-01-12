# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from collections import defaultdict
import json

import os
import logging
import threading
from time import sleep
from inventorum_ebay.tests.utils import AssertionMixin

from django.conf import settings

from inventorum_ebay.tests import StagingTestAccount
from django.test.testcases import LiveServerThread, LiveServerTestCase
from inventorum_ebay.apps.auth.models import EbayTokenModel
from inventorum_ebay.lib.ebay.authentication import EbayToken
from inventorum_ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory
from rest_framework.test import APILiveServerTestCase


log = logging.getLogger(__name__)


class ConcurrentLiveServerTestCase(AssertionMixin, APILiveServerTestCase):
    ports = [8100 + i for i in range(0, 10)]

    def setUp(self):
        super(ConcurrentLiveServerTestCase, self).setUp()
        self._ensure_ebay_authenticated_user()

    def _ensure_ebay_authenticated_user(self):
        self.account = EbayAccountFactory(inv_id=StagingTestAccount.ACCOUNT_ID,
                                          ebay_location_uuid='BB54CED9-2A34-480A-B187-11A97C4E15D4')
        self.user = EbayUserFactory(inv_id=StagingTestAccount.USER_ID, account=self.account)

        # Token valid till 2016.09.21 13:18:38
        self.ebay_token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE,
                                    site_id=settings.EBAY_SUPPORTED_SITES['DE'])
        self.account.token = EbayTokenModel.create_from_ebay_token(self.ebay_token)
        self.account.save()

    @property
    def credentials(self):
        return {
            "X-Inv-Account": self.user.account.inv_id,
            "X-Inv-User": self.user.inv_id
        }

    def url_for(self, port, path):
        return "http://%s:%s%s" % (self.host, port, path)

    @classmethod
    def setUpClass(cls):
        super(ConcurrentLiveServerTestCase, cls).setUpClass()

        # Launch the live server's thread
        specified_address = os.environ.get(
            'DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:8081')
        cls.host, port = specified_address.split(':')

        cls.server_threads = []
        for port in cls.ports:
            thread = LiveServerThread(cls.host, [port], static_handler=LiveServerTestCase.static_handler)
            thread.daemon = True
            thread.start()
            cls.server_threads.append(thread)

        # Wait for the live server to be ready
        for thread in cls.server_threads:
            thread.is_ready.wait()

            if thread.error:
                raise thread.error


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class ThreadedCoreAPIFake(threading.Thread):
    GET = "GET"
    POST = "POST"

    class FakeResponse(object):
        def __init__(self, status, body=None):
            self.status = status
            self.body = body

        @property
        def has_body(self):
            return self.body is not None

        @property
        def json(self):
            return json.dumps(self.body)

    _responses = defaultdict(dict)

    def __init__(self, host, port):
        super(ThreadedCoreAPIFake, self).__init__()

        self.host = host
        self.port = port

        class CoreAPIFake(BaseHTTPRequestHandler):

            def do_GET(s):
                s._handle(self.GET)

            def do_POST(s):
                s._handle(self.POST)

            def _handle(s, method):
                path = s.path
                if path not in self._responses[method]:
                    log.error("Unexpected %s: %s" % (method, path))
                    s.send_response(500)
                    return

                response = self._responses[method][path]

                sleep(1)

                s.send_response(response.status)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                if response.has_body:
                    s.wfile.write(response.json)
                s.wfile.close()

        self.server = ThreadedHTTPServer((host, port), CoreAPIFake)

    def whenGET(self, path, status, body=None):
        """
        :type path: unicode
        :type respond_with: dict
        """
        self._responses[self.GET][path] = self.FakeResponse(status, body)

    def whenPOST(self, path, status, body=None):
        """
        :type path: unicode
        :type respond_with: dict
        """
        self._responses[self.POST][path] = self.FakeResponse(status, body)

    def run(self, daemon=False):
        log.info('Starting core api fake server on %s:%s', self.host, self.port)
        self.server.serve_forever()

    def stop(self):
        log.info('Stopping core api fake server on %s:%s', self.host, self.port)
        self.server.shutdown()
