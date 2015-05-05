# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_auto_20150505_1653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebayitemimagemodel',
            name='inv_id',
        ),
        migrations.RemoveField(
            model_name='ebayitemvariationmodel',
            name='inv_id',
        ),
    ]
