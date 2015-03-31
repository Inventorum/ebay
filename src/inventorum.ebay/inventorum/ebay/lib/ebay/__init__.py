# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection

from django.conf import settings
from ebaysdk.parallel import Parallel

log = logging.getLogger(__name__)

EBAY_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class EbayException(Exception):
    pass


class EbayConnectionException(EbayException):
    pass


class EbayReturnedErrorsException(EbayException):
    pass


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
    error_lang = None

    def __init__(self, token=None, site_id=77, error_lang="en_US", parallel=None):
        self.api = Connection(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                              certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                              debug=settings.DEBUG, timeout=self.timeout, compatibility=self.compatibility,
                              version=self.version, parallel=parallel, config_file=None)

        self.token = token
        self.site_id = site_id
        self.error_lang = error_lang


    # EBAY PROPERTIES
    @property
    def token(self):
        return self.api.config.get('token')

    @token.setter
    def token(self, new_value):
        self.api.config.set('token', new_value, force=True)

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
        :return: dict Response from ebay
        """
        try:
            response = self.api.execute(verb=verb, data=data)
        except ConnectionError as e:
            log.error('Got ebay error: %s', e)
            raise EbayConnectionException(e)

        if self.api.error():
            raise EbayReturnedErrorsException(self.api.error())

        execution = EbayResponse(response)

        return execution.dict()


class EbayParallel(Ebay):
    executions = []
    parallel = None

    def __init__(self, *args, **kwargs):
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
        :return: EbayResponse Will be validated only after you call `wait()`
        """
        api = self.parallel_api_constructor().api
        api.execute(verb=verb, data=data)

        self.executions.append(api)

        return api

    def wait(self):
        """
        Executes all requests to ebay api at once.
        :return:
        """
        self.parallel.wait(self.timeout)
        return [EbayResponse(a.response) for a in self.executions]

    def wait_and_validate(self):
        """
        Executes all requests to ebay api at once and validates results.
        Throws EbayExceptions!
        :return:
        """
        rt = self.wait()

        if self.parallel.error():
            raise EbayReturnedErrorsException(self.parallel.error())

        return rt
