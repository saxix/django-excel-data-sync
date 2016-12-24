# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging

import pytest
from django.db.models import BooleanField, NullBooleanField
from example.models import DemoModel
from excel_data_sync.columns import get_column
# from excel_data_sync.inspector import process_model
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


def test_validator_booleanfield():
    c = get_column(BooleanField())
    v = c._get_validation()
    assert v['validate'] == 'list'
    assert v['value'] == ["True", "False"]


def test_validator_nullbooleanfield():
    c = get_column(NullBooleanField())
    v = c._get_validation()
    assert v['validate'] == 'list'
    assert v['value'] == ["", "True", "False"]


@pytest.mark.parametrize("field", ["boolean", "null_boolean"])
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
