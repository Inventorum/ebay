# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException

from inventorum.ebay.lib.rest.resources import APIResource
from requests.exceptions import HTTPError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


log = logging.getLogger(__name__)


class PublishResource(APIResource):

    def post(self, request, inv_product_id):
        service = PublishingService(inv_product_id, request.user)
        try:
            service.validate()
        except PublishingValidationException as e:
            raise ValidationError(e.message)

        service.prepare()
        return Response(data=core_product.name)

        # TODO:
        # 1. sync: aggregate data, construct "ebay listing" (take from core product and ebay service)
        # 2. sync: validate "ebay listing"
        #   - is not already published
        #   *- has billing address
        #   *- has shipping services
        #   *- has price >= 1
        #   *- has category
        # 3. async: publish ebay listing


# @inventorum_task(disable_events=[EntityUpdateProducer.event_type])
# def product_import_task(self, import_id):
#     """ entry point for async product import (executed in celery context) """
#     import_job = ProductImportModel.objects.get(pk=import_id)
#     log.info('Start processing product import job: %s, %s', import_job.id, import_job.file_size,
#              extra={'rid': import_job.rid})
#
#     service = ProductImportService(import_job)
#     try:
#         service.run()
#     except (ParserException, ImporterException) as e:
#         log.info("Product import job %s failed (rid:%s): %s", import_id, import_job.rid, e.message,
#                   extra={'rid': import_job.rid})
