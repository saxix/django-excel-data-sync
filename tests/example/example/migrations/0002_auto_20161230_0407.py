# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 03:07
from __future__ import unicode_literals

import datetime

import concurrency.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demomodel',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
        ),
        migrations.AlterField(
            model_name='demomodel',
            name='date_range',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2000, 1, 1)), django.core.validators.MaxValueValidator(datetime.date(2000, 12, 31))]),
        ),
    ]