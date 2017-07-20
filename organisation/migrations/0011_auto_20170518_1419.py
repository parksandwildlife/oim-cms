# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-18 06:19
from __future__ import unicode_literals

from django.db import migrations, models
import organisation.models


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0010_auto_20170515_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentuser',
            name='employee_id',
            field=models.CharField(blank=True, help_text='HR Employee ID. Enter n/a if no ID provided', max_length=128, null=True, unique=True, validators=[organisation.models.validate_employee_id], verbose_name='Employee ID'),
        ),
    ]
