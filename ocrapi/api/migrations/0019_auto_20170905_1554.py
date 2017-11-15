# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-05 15:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_file_rotation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analyzedimage',
            name='url',
        ),
        migrations.AlterField(
            model_name='analyzedimage',
            name='orders',
            field=models.TextField(default={}, verbose_name='user orders'),
            preserve_default=False,
        ),
    ]
