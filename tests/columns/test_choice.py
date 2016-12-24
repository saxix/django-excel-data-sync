# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from example.management.demo import factory
from example.models import DemoModel
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_write_xls():
    factory(choices=2)

    exp_filename = get_target_xls('cols/choices.xls')
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel,
                          fields=['choices'],
                          queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp

    from xlrd import open_workbook
    wb = open_workbook(exp_filename)
    sheet = wb.sheets()[0]
    cell_value = sheet.cell(1, 0).value
    assert cell_value == 'Choice 2'
