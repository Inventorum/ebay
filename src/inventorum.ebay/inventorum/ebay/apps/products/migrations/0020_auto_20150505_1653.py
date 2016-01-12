# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_ids(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.

    EbayItemImageModel = apps.get_model("products", "EbayItemImageModel")
    for image in EbayItemImageModel.objects.all():
        image.inv_image_id = image.inv_id
        image.save()

    EbayItemVariationModel = apps.get_model("products", "EbayItemVariationModel")
    for product in EbayItemVariationModel.objects.all():
        product.inv_product_id = product.inv_id
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_ebayitemimagemodel_inv_image_id'),
    ]

    operations = [
        migrations.RunPython(migrate_ids)
    ]
