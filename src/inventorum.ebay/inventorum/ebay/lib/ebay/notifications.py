# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import base64
import hashlib
import datetime

from ebaysdk.response import ResponseDataObject, Response
from inventorum.ebay.lib.ebay.data import EbayParser


log = logging.getLogger(__name__)


class EbayNotification(object):
    """
    Parses, validates, and represents an ebay platform notification according to
    http://developer.ebay.com/Devzone/guides/ebayfeatures/Notifications/Notifications.html
    """
    class ParseError(Exception):
        pass

    class SignatureValidationError(Exception):
        pass

    SOAP_ACTION_HEADER = "HTTP_SOAPACTION"
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    request_headers = None
    request_body = None

    event_type = None
    payload = None
    timestamp = None
    signature = None

    def __init__(self, headers, body):
        """
        :param headers: The HTTP request headers
        :type headers: dict[unicode, unicode]

        :param body: The HTTP request body
        :type body: unicode
        """
        self.request_headers = headers
        self.request_body = body

        self._parse_request_headers()
        self._parse_request_body()

    def _parse_request_headers(self):
        soap_action = self.request_headers.get(self.SOAP_ACTION_HEADER, None)
        if soap_action is None:
            raise self.ParseError("Required header `{}` not found".format(self.SOAP_ACTION_HEADER))

        # header contains a URL that ends with the name of the event that the notification is being sent for
        # e.g. "https://developer.ebay.com/notification/FixedPriceTransaction"
        self.event_type = soap_action.replace("\"", "").split("/").pop()

    def _parse_request_body(self):
        # We can re-use ebaysdk's response parsing here, as notification bodies are valid ebay responses
        try:
            data_object = ResponseDataObject({'content': self.request_body}, [])
            parser = Response(data_object)
            envelop = parser.dict()["Envelope"]

            message_header, message_body = envelop["Header"], envelop["Body"]

            # The message body contains a top-level element that is named after the call used to generate the data with
            # the word Response at the end, e.g. the payload element name for the ItemSold event is GetItemResponse
            payload = None
            for key, value in message_body.iteritems():
                if key.endswith("Response"):
                    # Remove trailing Response
                    payload = value

            if payload is None:
                raise self.ParseError("No response body found")

            self.payload = payload
            self.signature = message_header['RequesterCredentials']['NotificationSignature']
            self.timestamp = self.payload['Timestamp']
        except (KeyError, AttributeError) as e:
            raise self.ParseError(e.message)

    def validate_signature(self, ebay_dev_id, ebay_app_id, ebay_cert_id):
        """
        Validates the signature according to
        http://developer.ebay.com/Devzone/guides/ebayfeatures/Notifications/Notifications.html#SOAPMessageHeaderNotificationSignature

        :type ebay_dev_id: str
        :type ebay_app_id: str
        :type ebay_cert_id: str
        """
        # First, we validate whether the timestamp is within 10 minutes of the actual time in GMT
        sent_at = EbayParser.parse_date(self.timestamp)
        utc_now = datetime.datetime.utcnow()

        if utc_now - sent_at > datetime.timedelta(minutes=10):
            raise self.SignatureValidationError("Notification expired")

        # If yes, we validate the actual signature using the given timestamp
        base64hash = self.compute_signature(self.timestamp, ebay_dev_id, ebay_app_id, ebay_cert_id)
        if base64hash != self.signature:
            raise self.SignatureValidationError("Hash mismatch")

    @classmethod
    def compute_signature(cls, timestamp, ebay_dev_id, ebay_app_id, ebay_cert_id):
        """
        Computes the notification signature hash according to
        http://developer.ebay.com/Devzone/guides/ebayfeatures/Notifications/Notifications.html#SOAPMessageHeaderNotificationSignature

        :type timestamp: str
        :type ebay_dev_id: str
        :type ebay_app_id: str
        :type ebay_cert_id: str

        :rtype: str
        """
        _hash = ''.join([timestamp, ebay_dev_id, ebay_app_id, ebay_cert_id]).encode()
        m = hashlib.md5()
        m.update(_hash)
        md5hash = m.digest()
        return base64.standard_b64encode(md5hash)
