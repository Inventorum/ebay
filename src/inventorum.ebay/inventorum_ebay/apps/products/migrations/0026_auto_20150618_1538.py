# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_core_product_id(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    EbayItemModel = apps.get_model("products", "EbayItemModel")

    for item in EbayItemModel.objects.all():
        item.inv_product_id = item.product.inv_id
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_ebayitemmodel_inv_product_id'),
    ]

    operations = [
        migrations.RunPython(set_core_product_id),
    ]
