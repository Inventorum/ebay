# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_auto_20150415_1623'),
    ]

    operations = [
        migrations.RunSQL('CREATE INDEX ix_categories_categorymodel_tree_id ON categories_categorymodel (tree_id)',
                          'DROP INDEX ix_categories_categorymodel_tree_id'),

        migrations.RunSQL('CREATE INDEX ix_categories_categorymodel_name_and_parent_id ON categories_categorymodel (name, parent_id)',
                          'DROP INDEX ix_categories_categorymodel_name_and_parent_id')
    ]
