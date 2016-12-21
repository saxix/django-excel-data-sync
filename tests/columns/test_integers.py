# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.models import (BigIntegerField, Field, IntegerField,
                              PositiveIntegerField, PositiveSmallIntegerField,
                              SmallIntegerField,)
from excel_data_sync.columns import get_column

logger = logging.getLogger(__name__)


def test_validation():
    f = Field('Field1')
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'any'


@pytest.mark.parametrize("field", [SmallIntegerField, IntegerField, BigIntegerField,
                                   PositiveSmallIntegerField, PositiveIntegerField, ])
def test_validator_number_base(field):
    f = field()
    limits = BaseDatabaseOperations.integer_field_ranges[f.get_internal_type()]
    v = get_column(f)._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)))'
    assert v["error_message"] == "Enter a value between {} and {}".format(*limits)


@pytest.mark.parametrize("field", [SmallIntegerField, IntegerField, BigIntegerField,
                                   PositiveSmallIntegerField, PositiveIntegerField, ])
def test_validator_number_min_value(field):
    f = field(validators=[MinValueValidator(100)])
    limits = 100, BaseDatabaseOperations.integer_field_ranges[f.get_internal_type()][1]
    v = get_column(f)._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),VALUE(THIS)>=100)'
    assert v["error_message"] == "Enter a value between {} and {}".format(*limits)


@pytest.mark.parametrize("field", [SmallIntegerField, IntegerField, BigIntegerField,
                                   PositiveSmallIntegerField, PositiveIntegerField, ])
def test_validator_number_max_value(field):
    f = field(validators=[MinValueValidator(100), MaxValueValidator(200)])
    limits = 100, 200
    v = get_column(f)._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),VALUE(THIS)>=100,VALUE(THIS)<=200)'
    assert v["error_message"] == "Enter a value between {} and {}".format(*limits)
