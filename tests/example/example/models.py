# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from six import python_2_unicode_compatible

from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from excel_data_sync.columns import NumberColumn, register_column


@python_2_unicode_compatible
class Option(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'example'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class DemoModel(models.Model):
    CHOICES = ((1, 'Choice 1'), (2, 'Choice 2'), (3, 'Choice 3'))
    # base
    char = models.CharField('Chäř', max_length=30)
    integer = models.IntegerField()
    positive_integer = models.PositiveIntegerField()
    max_value_10 = models.IntegerField(validators=[MaxValueValidator(10)])
    range_5_10 = models.IntegerField(validators=[MinValueValidator(5),
                                                 MaxValueValidator(10)])
    boolean = models.BooleanField(default=False)
    choices = models.IntegerField(choices=CHOICES)
    unique = models.CharField(max_length=255, unique=True)

    uuid = models.UUIDField(blank=True, null=True)
    small_integer = models.SmallIntegerField(default=1)
    positive_small_integer = models.PositiveSmallIntegerField()
    null_boolean = models.NullBooleanField(default=None)
    date_range = models.DateField(validators=[MinValueValidator(datetime(2000, 1, 1).date()),
                                              MaxValueValidator(datetime(2000, 12, 31).date()),
                                              ])
    date = models.DateField()
    datetime = models.DateTimeField()
    time = models.TimeField()
    decimal = models.DecimalField(max_digits=10, decimal_places=3)
    email = models.EmailField()
    float = models.FloatField()
    big_integer = models.BigIntegerField()
    generic_ip = models.GenericIPAddressField()
    url = models.URLField()
    text = models.TextField()

    required = models.CharField(max_length=255, null=False, blank=False)
    nullable = models.CharField(max_length=255, null=True, blank=True)
    blank = models.CharField(max_length=255, blank=True, null=True)
    not_editable = models.CharField(max_length=255, editable=False, blank=True, null=True)

    option = models.ForeignKey(Option)
    # extras
    version = IntegerVersionField()

    class Meta:
        app_label = 'example'

    def __str__(self):
        return str(self.id)


@python_2_unicode_compatible
class UserDetail(models.Model):
    user = models.ForeignKey(User)
    note = models.CharField(max_length=10, blank=True)

    class Meta:
        app_label = 'example'

    def __str__(self):
        return str(self.id)


class VBAColumn(NumberColumn):
    need_vba = True


class DemoModelVBA(models.Model):
    col1 = models.IntegerField()
    col2 = models.IntegerField()

    class Meta:
        app_label = 'example'


register_column('example.demomodelvba.col1', VBAColumn)
register_column('example.demomodelvba.col2', VBAColumn)
