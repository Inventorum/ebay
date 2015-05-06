# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal

from django.db import migrations


def provide_tax_rate_for_existing_ebay_item_models(apps, schema_editor):
    EbayItemModel = apps.get_model("products", "EbayItemModel")
    EbayItemVariationModel = apps.get_model("products", "EbayItemVariationModel")

    for item_model in EbayItemModel.objects.all():
        item_model.tax_rate = Decimal("19")
        item_model.save()

    for item_variation_model in EbayItemVariationModel.objects.all():
        item_variation_model.tax_rate = Decimal("19")
        item_variation_model.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_auto_20150506_1136'),
    ]

    operations = [
        migrations.RunPython(provide_tax_rate_for_existing_ebay_item_models),
    ]
