# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.lib.ebay.data.events import EbayEventResponse
import requests


class EbayInboundEventsException(Exception):
    def __init__(self, errors, response):
        """
        :type errors:  list[inventorum_ebay.lib.ebay.data.events.EbayEventError]
        :type response: EbayEventResponse
        """
        self.errors = errors
        self.response = response

    @property
    def message(self):
        return "\n".join([unicode(e) for e in self.errors])


class EbayInboundEvents(object):
    HEADER_EVENT_TYPE = 'X-EBAY-EVENT-TYPE'
    url = 'https://svcs.ebay.com/eventbridge/InboundEvent/publish'

    def __init__(self, ebay_token):
        """
        :type ebay_token: inventorum_ebay.lib.ebay.data.authorization.EbayToken
        :return:
        """
        self.ebay_token = ebay_token

    def publish(self, event, raise_exceptions=True):
        """
        :type event: inventorum_ebay.lib.ebay.data.events.EbayEventBase
        :return:
        """

        data = self.build_request_payload(event)

        headers = self._default_headers
        headers[self.__class__.HEADER_EVENT_TYPE] = event.type

        response = requests.post(self.url, json=data, headers=headers)
        event_response = self.parse_response(response)
        if raise_exceptions and not event_response.ack:
            raise EbayInboundEventsException(event_response.errors, event_response)

        return event_response

    @property
    def _default_headers(self):
        return {
            'Authorization': 'TOKEN {token}'.format(token=self.ebay_token.value),
            'Content-Type': 'application/json'  # type of request only, response is always XML
        }

    def build_request_payload(self, event):
        """
        :type payload: inventorum_ebay.lib.ebay.data.events.EbayEventBase
        :return: dict
        """
        return {
            "event": {
                "version": "1.0",
                "type": event.type,
                "notifierReferenceId": "test",
                "payload": event.payload
            }
        }

    def parse_response(self, response):
        """
        :type response: requests.models.Response
        :rtype: inventorum_ebay.lib.ebay.data.events.EbayEventResponse
        """
        return EbayEventResponse.Deserializer(data=response.json()).build()
