# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0032_ebayitemmodel_return_policy'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ebayitemimagemodel',
            options={'ordering': ('time_added', 'id')},
        ),
        migrations.RenameField(
            model_name='ebayitemvariationupdatemodel',
            old_name='is_deleted',
            new_name='is_variation_deleted',
        ),
        migrations.RemoveField(
            model_name='ebayapiattempt',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayapiattemptrequest',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayapiattemptresponse',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemimagemodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitempaymentmethod',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemshippingdetails',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemspecificmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemupdatemodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemvariationmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemvariationspecificmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemvariationspecificvaluemodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayitemvariationupdatemodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayproductmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayproductspecificmodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='ebayapiattempt',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayapiattemptrequest',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayapiattemptresponse',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemimagemodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitempaymentmethod',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemshippingdetails',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemspecificmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemupdatemodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemvariationmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemvariationspecificmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemvariationspecificvaluemodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemvariationupdatemodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayproductmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayproductspecificmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
