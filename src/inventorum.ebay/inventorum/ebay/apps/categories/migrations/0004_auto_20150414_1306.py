# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_auto_20150407_1423'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorymodel',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='categorymodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='categorymodel',
            name='time_added',
        ),
        migrations.RemoveField(
            model_name='categorymodel',
            name='time_modified',
        ),
        migrations.AlterField(
            model_name='categorymodel',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='categories.CategoryModel', null=True),
            preserve_default=True,
        ),
    ]
