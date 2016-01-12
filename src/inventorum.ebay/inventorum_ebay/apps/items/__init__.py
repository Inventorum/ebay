from __future__ import absolute_import, unicode_literals
from django.conf import settings as django_settings


class EbaySKU(object):
    @classmethod
    def get_env_prefix(cls):
        """
        Gets the environment variable as prefix out of the SKU_FORMAT from settings.
        :return: environment as unicode
        :rtype: unicode
        """
        return django_settings.EBAY_SKU_FORMAT.format('')

    @classmethod
    def extract_product_id(cls, sku):
        """
        Extracts Inventorum product id from sku.
        :type sku: unicode
        :rtype: unicode
        """
        return sku.replace(cls.get_env_prefix(), '')

    @classmethod
    def belongs_to_current_env(cls, sku):
        """
        Checks, if item.sku fits into the current environment.
        :param sku: unicode
        :return: belongs to current environment as boolean
        :rtype boolean
        """
        return sku.startswith(cls.get_env_prefix())

    @classmethod
    def generate_sku(cls, product_id):
        """
        Generates sku out of product_id which can be also the inv_id.
        :param product_id: product_id as unicode
        :return: sku as unicode
        :rtype unicode
        """
        return '%s%s' % (cls.get_env_prefix(), product_id)
