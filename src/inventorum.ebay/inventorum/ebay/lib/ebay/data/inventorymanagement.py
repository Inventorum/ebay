# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers


class EbayInterval(object):
    def __init__(self, open, close):
        self.open = open
        self.close = close

    def dict(self):
        return {
            'Open': self.open,
            'Close': self.close
        }


class EbayDay(object):
    def __init__(self, day_of_week, intervals):
        """
        :type day_of_week: int
        :typ intervals: list[EbayInterval]
        :return:
        """
        self.day_of_week = day_of_week
        self.intervals = intervals

    def dict(self):
        return {
            'DayOfWeek': self.day_of_week,
            'Interval': [i.dict() for i in self.intervals]
        }


class EbayLocation(object):
    def __init__(self, location_id, address1, city, country, days, latitude, longitude, name, phone, postal_code,
                 region, utc_offset, url=None, address2=None, pickup_instruction=None, location_type="STORE"):
        """
        :type location_id: unicode
        :type address1: unicode
        :type city: unicode
        :type country: unicode
        :type days: list[EbayDay]
        :type latitude: decimal.Decimal
        :type longitude: decimal.Decimal
        :type name: unicode
        :type phone: unicode
        :type postal_code: unicode
        :type region: unicode
        :type utc_offset: unicode
        :type url: unicode | None
        :type address2: unicode | None
        :type pickup_instruction: unicode | None
        :type location_type: unicode
        """
        self.location_id = location_id
        self.address1 = address1
        self.city = city
        self.country = country
        self.days = days
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.phone = phone
        self.postal_code = postal_code
        self.region = region
        self.utc_offset = utc_offset
        self.url = url
        self.address2 = address2
        self.pickup_instruction = pickup_instruction
        self.location_type = location_type

    def dict(self):
        data = {
            'Address1': self.address1,
            'City': self.city,
            'Country': self.country,
            'Hours': {'Day': [day.dict() for day in self.days]},
            'Latitude': self.latitude,
            'Longitude': self.longitude,
            'LocationID': self.location_id,
            'LocationType': self.location_type,
            'Name': self.name,
            'Phone': self.phone,
            'PostalCode': self.postal_code,
            'Region': self.region,
            'UTCOffset': self.utc_offset,
        }

        if self.address2 is not None:
            data['Address2'] = self.address2

        if self.url is not None:
            data['URL'] = self.url

        if self.pickup_instruction is not None:
            data['PickupInstructions'] = self.pickup_instruction

        return data


class EbayAvailability(object):
    IN_STOCK = "IN_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    SHIP_TO_STORE = "SHIP_TO_STORE"


class EbayLocationAvailability(object):
    def __init__(self, availability, location_id, quantity):
        self.availability = availability
        self.location_id = location_id
        self.quantity = quantity

    def dict(self):
        data = {
            "Availability": self.availability,
            "LocationID": self.location_id,
        }
        if self.quantity is not None:
            data["Quantity"] = int(self.quantity)
        return data


class EbayAddLocationResponse(object):
    def __init__(self, location_id):
        """
        :type location_id: unicode
        :return:
        """
        self.location_id = location_id


class EbayAddLocationResponseDeserializer(POPOSerializer):
    LocationID = serializers.CharField(source="location_id")

    class Meta:
        model = EbayAddLocationResponse


class EbayAddDeleteInventoryResponse(object):
    def __init__(self, sku):
        """
        :type sku: unicode
        :return:
        """
        self.sku = sku


class EbayAddDeleteInventoryResponseDeserializer(POPOSerializer):
    SKU = serializers.CharField(source="sku")

    class Meta:
        model = EbayAddDeleteInventoryResponse


class EbayDeleteInventoryLocationResponse(object):
    def __init__(self, location_id):
        """
        :type location_id: unicode
        :return:
        """
        self.location_id = location_id


class EbayDeleteInventoryLocationDeserializer(POPOSerializer):
    LocationID = serializers.CharField(source="location_id")

    class Meta:
        model = EbayDeleteInventoryLocationResponse