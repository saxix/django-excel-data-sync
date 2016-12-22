# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging

import pytest
from example.models import DemoModel
from excel_data_sync.inspector import process_model
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_validator_foreignkey(data):
    exp_filename = get_target_xls('test_foreignkey.xlsx')
    io = get_io(exp_filename)
    process_model(DemoModel, io,
                  fields=['id', 'option'],
                  properties={'title': 'Title'})
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
