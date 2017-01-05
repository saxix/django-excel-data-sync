# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.models import (BigIntegerField, Field, IntegerField,
                              PositiveIntegerField, PositiveSmallIntegerField,
                              SmallIntegerField,)
from example.models import DemoModel
from excel_data_sync.columns import get_column
# from excel_data_sync.inspector import process_model
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


def test_validation():
    f = Field('Field1', blank=True)
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'any'


@pytest.mark.parametrize("field", [SmallIntegerField, IntegerField, BigIntegerField,
                                   PositiveSmallIntegerField, PositiveIntegerField, ])
def test_validator_number_base(field):
    f = field(blank=True)
    limits = BaseDatabaseOperations.integer_field_ranges[f.get_internal_type()]
    v = get_column(f)._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),VALUE(THIS)>={},VALUE(THIS)<={})'.format(*limits)
    assert v["error_message"] == "Enter a value between {} and {}".format(*limits)


@pytest.mark.parametrize("field", [SmallIntegerField, IntegerField, BigIntegerField,
                                   PositiveSmallIntegerField, PositiveIntegerField, ])
def test_validator_number_min_value(field):
    f = field(blank=True, validators=[MinValueValidator(100)])
    limits = 100, BaseDatabaseOperations.integer_field_ranges[f.get_internal_type()][1]
    v = get_column(f)._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),VALUE(THIS)>={},VALUE(THIS)<={})'.format(*limits)
    assert v["error_message"] == "Enter a value between {} and {}".format(*limits)


@pytest.mark.parametrize("field", [SmallIntegerField, IntegerField, BigIntegerField,
                                   PositiveSmallIntegerField, PositiveIntegerField, ])
def test_validator_number_max_value(field):
    f = field(blank=True, validators=[MinValueValidator(100), MaxValueValidator(200)])
    limits = 100, 200
    v = get_column(f)._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),VALUE(THIS)>={},VALUE(THIS)<={})'.format(*limits)
    assert v["error_message"] == "Enter a value between {} and {}".format(*limits)


@pytest.mark.parametrize("field", ["small_integer", "integer", "big_integer",
                                   "positive_small_integer", "positive_integer", ])
@pytest.mark.django_db
def test_write_xls(field):
    exp_filename = get_target_xls('cols/{}.xls'.format(field))
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel,
                          fields=[field])
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
