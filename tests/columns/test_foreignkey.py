# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging

import pytest
# from example.models import DemoModel
# from excel_data_sync.inspector import process_model
from example.models import DemoModel
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_validator_foreignkey(data):
    exp_filename = get_target_xls('cols/foreignkey.xlsx')
    io = get_io(exp_filename)
    with XlsTemplate(io, properties={'title': 'Title'}) as xls:
        xls.process_model(DemoModel,
                          fields=['id', 'option'])
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
