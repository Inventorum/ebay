# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebaytokenmodel',
            name='site_id',
            field=models.IntegerField(default=77),
            preserve_default=True,
        ),
    ]
