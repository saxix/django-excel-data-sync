# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from django.db.models import AutoField

from example.models import DemoModel
from excel_data_sync.columns import get_column
from excel_data_sync.inspector import process_model
from helperfunctions import get_target_xls, get_io, _compare_xlsx_files

logger = logging.getLogger(__name__)

try:
    from django.db.models.fields import BigAutoField

    targets = [(AutoField, [2147483648, 2147483647]),
               (BigAutoField, [9223372036854775808, 9223372036854775807])]
except ImportError:
    targets = [(AutoField, [2147483648, 2147483647])]


@pytest.mark.parametrize("field,limits", targets)
def test_validator(field, limits):
    f = field()
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'custom'
    assert v['criteria'] == ''
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),VALUE(THIS)>=-{},VALUE(THIS)<={})'.format(*limits)


@pytest.mark.parametrize("field", ["id"])
@pytest.mark.django_db
def test_write_xls(field):
    exp_filename = get_target_xls('cols/{}.xls'.format(field))
    io = get_io(exp_filename)
    process_model(DemoModel, io,
                  fields=[field])
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
