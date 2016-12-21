# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from six import python_2_unicode_compatible


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
    logic = models.BooleanField(default=False)
    choices = models.IntegerField(choices=CHOICES)
    unique = models.CharField(max_length=255, unique=True)

    uuid = models.UUIDField(blank=True, null=True)
    small_integer = models.SmallIntegerField()
    positive_small_integer = models.PositiveSmallIntegerField()
    null_logic = models.NullBooleanField(default=None)
    date = models.DateField()
    datetime = models.DateTimeField()
    time = models.TimeField()
    decimal = models.DecimalField(max_digits=10, decimal_places=3)
    email = models.EmailField()
    float = models.FloatField()
    bigint = models.BigIntegerField()
    generic_ip = models.GenericIPAddressField()
    url = models.URLField()
    text = models.TextField()

    nullable = models.CharField(max_length=255, null=True, blank=True)
    blank = models.CharField(max_length=255, blank=True, null=True)
    not_editable = models.CharField(max_length=255, editable=False, blank=True, null=True)

    option = models.ForeignKey(Option)

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
