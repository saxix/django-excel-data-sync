# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from example.management.demo import factory
from example.models import DemoModel, Option
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_write_data_default_formats():
    exp_filename = get_target_xls('concurrency.xls')
    io = get_io(exp_filename)
    factory(option=Option.objects.get_or_create(name='Option 1')[0])

    options = {"default_date_format": 'YYYY MMM DD',
               "default_datetime_format": 'YYYY MM DD hh:mm',
               "default_time_format": 'hh.mm (ss)',
               }
    with XlsTemplate(io, options=options) as xls:
        xls.process_model(DemoModel,
                          fields=['id', 'version', 'char'],
                          queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename,
                                   ignore_elements={'xl/worksheets/sheet1.xml': ['<v>\d{10,}']}
                                   )

    assert got == exp
