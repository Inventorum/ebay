# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0004_auto_20150429_0036'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippingservicemodel',
            options={'ordering': ('description', 'id')},
        ),
        migrations.RemoveField(
            model_name='shippingservicemodel',
            name='is_international',
        ),
    ]
