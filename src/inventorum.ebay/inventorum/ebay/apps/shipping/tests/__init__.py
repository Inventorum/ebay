# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal as D

from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.apps.shipping.tests.factories import ShippingServiceFactory
from inventorum.ebay.tests import Countries
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


class ShippingServiceTestMixin(object):

    def get_shipping_service_dhl(self):
        """
        :returns: Shipping service "DE_DHL_Express" (get_or_create)
        :rtype: inventorum.ebay.apps.shipping.models.ShippingServiceModel
        """
        return ShippingServiceFactory.create(external_id="DE_DHLPaket",
                                             description="DHL Paket",
                                             shipping_time_min=1,
                                             shipping_time_max=3)

    def get_shipping_service_hermes(self):
        """
        :returns: Shipping service "DE_Hermes_Package" (get_or_create)
        :rtype: inventorum.ebay.apps.shipping.models.ShippingServiceModel
        """
        return ShippingServiceFactory.create(external_id="DE_HermesPaket",
                                             description="Hermes Paket")

    def get_shipping_service_ups(self):
        """
        :returns: Shipping service "DE_UPSExpress" (get_or_create)
        :rtype: inventorum.ebay.apps.shipping.models.ShippingServiceModel
        """
        return ShippingServiceFactory.create(external_id="DE_UPSExpress",
                                             description="UPS Express")

    def get_shipping_service_click_and_collect(self, country=Countries.DE):
        return ShippingServiceModel.get_click_and_collect_service(country)

    def get_shipping_services(self):
        """
        :returns: List of shipping services "DE_DHL_Express", "DE_Hermes_Package", "DE_UPS_International"
        :rtype: inventorum.ebay.apps.shipping.models.ShippingServiceModel
        """
        return [self.get_shipping_service_dhl(), self.get_shipping_service_hermes(), self.get_shipping_service_ups()]


class ShippingServiceConfigurableSerializerTest(ShippingServiceTestMixin):

    # Required interface for implementing test classes -----------------------

    def get_entity(self):
        raise NotImplemented

    def get_serializer_class(self):
        raise NotImplemented

    # Test methods -----------------------------------------------------------

    def test_shipping_service_create_update_delete(self):
        entity = self.get_entity()
        assert entity.shipping_services.count() == 0

        dhl = self.get_shipping_service_dhl()
        hermes = self.get_shipping_service_hermes()
        ups = self.get_shipping_service_ups()

        # assign to shipping services
        dhl_data = {"service": dhl.pk,
                    "cost": "1.49",
                    "additional_cost": "0.00"}

        hermes_data = {"service": hermes.pk,
                       "cost": "4.99",
                       "additional_cost": "1.99"}

        ups_data = {"service": ups.pk,
                    "cost": "19.99",
                    "additional_cost": "0.00"}

        self._partial_shipping_services_update(entity, [dhl_data, hermes_data])

        self.assertEqual(entity.shipping_services.count(), 2)

        dhl_config = entity.shipping_services.get(service_id=dhl.id)
        self.assertEqual(dhl_config.cost, D("1.49"))
        self.assertEqual(dhl_config.additional_cost, D("0.00"))

        hermes_config = entity.shipping_services.get(service_id=hermes.id)
        self.assertEqual(hermes_config.cost, D("4.99"))
        self.assertEqual(hermes_config.additional_cost, D("1.99"))

        # update dhl, remove hermes and add ups instead
        dhl_update_data = {"service": dhl.pk,
                           "cost": "1.79",
                           "additional_cost": "0.30"}

        self._partial_shipping_services_update(entity, [dhl_update_data, ups_data])

        self.assertEqual(entity.shipping_services.count(), 2)

        dhl_config = entity.shipping_services.get(service_id=dhl.id)
        self.assertEqual(dhl_config.cost, D("1.79"))
        self.assertEqual(dhl_config.additional_cost, D("0.30"))

        ups_config = entity.shipping_services.get(service_id=ups.id)
        self.assertEqual(ups_config.cost, D("19.99"))
        self.assertEqual(ups_config.additional_cost, D("0.00"))

        # delete all
        self._partial_shipping_services_update(entity, [])

        self.assertEqual(entity.shipping_services.count(), 0)

    def test_shipping_service_validation(self):
        entity = self.get_entity()

        # try to assign with invalid service pk
        invalid_data = {"shipping_services": [{"service": 99999,
                                               "cost": "1.99",
                                               "additional_cost": "2.99"}]}

        subject = self.get_serializer_class()(entity, data=invalid_data, partial=True)
        with self.assertRaises(ValidationError):
            subject.is_valid(raise_exception=True)

        self.assertEqual(subject.errors, {"shipping_services": [
            {"service": ['Invalid pk "99999" - object does not exist.']}]})

        # try to assign shipping service of different county
        assert self._get_country_from_entity(entity) == Countries.DE

        dhl_AT = self.get_shipping_service_dhl()
        dhl_AT.country = Countries.AT
        dhl_AT.save()

        invalid_data = {"shipping_services": [{"service": dhl_AT.id,
                                               "cost": "1.99",
                                               "additional_cost": "2.99"}]}

        subject = self.get_serializer_class()(entity, data=invalid_data, partial=True)
        with self.assertRaises(ValidationError):
            subject.is_valid(raise_exception=True)

    def test_uniqueness_of_shipping_services(self):
        entity = self.get_entity()
        assert entity.shipping_services.count() == 0

        dhl = ShippingServiceFactory.create(external_id="DE_DHL_Express")

        dhl_data_1 = {"service": dhl.pk,
                      "cost": "1.49",
                      "additional_cost": "0.00"}

        dhl_data_2 = {"service": dhl.pk,
                      "cost": "3.99",
                      "additional_cost": "1.00"}

        self._partial_shipping_services_update(entity, [dhl_data_1, dhl_data_2])

        self.assertEqual(entity.shipping_services.count(), 1)

        # last one wins :-)
        service_config = entity.shipping_services.first()
        self.assertEqual(service_config.cost, D("3.99"))
        self.assertEqual(service_config.additional_cost, D("1.00"))

    # Test helpers -----------------------------------------------------------

    def _partial_shipping_services_update(self, entity, shipping_services_data):
        """
        :type entity: inventorum.ebay.apps.shipping.models.ShippingServiceConfigurable
        :type shipping_services_data: list[dict]
        """
        data = {"shipping_services": shipping_services_data}

        subject = self.get_serializer_class()(entity, data=data, partial=True)
        subject.is_valid(raise_exception=True)
        subject.save()

    def _get_country_from_entity(self, entity):
        """
        :type entity: inventorum.ebay.apps.shipping.models.ShippingServiceConfigurable
        """
        if hasattr(entity, "country"):
            return entity.country
        elif hasattr(entity, "account"):
            return entity.account.country
        else:
            raise Exception("Cannot determine country")
