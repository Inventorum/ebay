# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from django.utils.datetime_safe import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection

from django.conf import settings
from ebaysdk.parallel import Parallel
from inventorum.ebay.lib.ebay.data.errors import EbayError

log = logging.getLogger(__name__)


class EbayException(Exception):
    pass


class EbayNotSupportedSite(EbayException):
    pass


class EbayConnectionException(EbayException):
    """
    :type errors: list[EbayError]
    """
    errors = None

    def __init__(self, message, response):
        self.message = message
        self.response = response
        if self.response is not None:
            errors = self.response.dict()['Errors']
            if not isinstance(errors, list):
                errors = [errors]
            self.errors = [EbayError.create_from_data(e) for e in errors]

    def __unicode__(self):
        return 'Message: %s ' % self.message


class EbayResponse(object):
    """
    Wrapper for return of Ebay API, so we can have our internal validation here etc. (easier use with Parallel)
    """
    validated = False

    def __init__(self, response):
        self.response = response

    def dict(self):
        return self.response.dict()


class Ebay(object):
    """
        Inventorum Ebay class with preconfiguration of Ebay Trading API.
    """
    # The newest version from Ebay Trading for 31 March 2015
    compatibility = 911
    version = 911
    timeout = 20
    api = None
    _token = None
    default_site_id = 77

    def __init__(self, token=None, default_site_id=None, parallel=None):

        self.api = Connection(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                              certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                              debug=settings.DEBUG, timeout=self.timeout, compatibility=self.compatibility,
                              version=self.version, parallel=parallel, config_file=None)

        if default_site_id is not None:
            self.default_site_id = default_site_id

        self.site_id = self.default_site_id

        self.token = token


    # EBAY PROPERTIES
    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, new_value):
        self._token = new_value
        value = getattr(self._token, 'value', None)
        self.api.config.set('token', value, force=True)

        # Set site id
        site_id = getattr(self._token, 'site_id', self.default_site_id)
        if site_id not in settings.EBAY_SUPPORTED_SITES.values():
            raise EbayNotSupportedSite()
        self.api.config.set('siteid', site_id, force=True)

    @property
    def site_id(self):
        return self.api.config.get('siteid')

    @site_id.setter
    def site_id(self, new_value):
        self.api.config.set('siteid', new_value, force=True)

    def execute(self, verb, data=None):
        """
        :param verb: Type of a API request
        :param data: Data that will be converted to XML and send to ebay
        :return: Response from ebay

        :type verb: str | unicode
        :type data: dict
        :rtype: dict
        """
        self._append_additional_params_to_data(data)
        try:
            response = self.api.execute(verb=verb, data=data)
        except ConnectionError as e:
            log.error('Got ebay error: %s', e)
            raise EbayConnectionException(e.message, e.response)

        execution = EbayResponse(response)

        return execution.dict()

    def _append_additional_params_to_data(self, data):
        if self._token:
            data['ErrorLanguage'] = self._token.error_language or "en_US"


class EbayParallel(Ebay):
    executions = None
    parallel = None

    def __init__(self, *args, **kwargs):
        self.executions = []
        self.parallel = kwargs.get('parallel')
        if not self.parallel:
            self.parallel = Parallel()
            kwargs['parallel'] = self.parallel

        self.parallel_api_constructor = lambda: Ebay(*args, **kwargs)
        super(EbayParallel, self).__init__(*args, **kwargs)

    def execute(self, verb, data=None):
        """
        Add to stack call to ebay api, to execute, you need to call `wait()`
        :param verb: Type of a API request
        :param data: Data that will be converted to XML and send to ebay
        :return: Will be validated only after you call `wait()`

        :type verb: str | unicode
        :type data: dict
        :rtype: Connection
        """
        self._append_additional_params_to_data(data)
        api = self.parallel_api_constructor().api
        api.execute(verb=verb, data=data)

        self.executions.append(api)

        return api

    def wait(self):
        """
        Executes all requests to ebay api at once.
        :return: List of EbayResponses
        :rtype: [EbayResponse]
        """
        self.parallel.wait(self.timeout)
        return [EbayResponse(a.response) for a in self.executions]

    def wait_and_validate(self):
        """
        Executes all requests to ebay api at once and validates results.
        Throws EbayExceptions!
        :return: List of EbayResponses
        :rtype: [EbayResponse]
        """
        rt = self.wait()

        if self.parallel.error():
            raise EbayConnectionException(self.parallel.error(), None)

        return rt
