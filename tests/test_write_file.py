# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
import pytz
from datetime import datetime
from xlrd import xldate_as_tuple

from example.management.demo import factory
from example.models import DemoModel, Option
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls, _check_format

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_write_template(data):
    exp_filename = get_target_xls('template.xls')
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel)

    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_data(data):
    exp_filename = get_target_xls('with_data.xls')
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel,
                          exclude=['email', 'option', 'uuid', 'version'],
                          queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_properties(data):
    exp_filename = get_target_xls('with_properties.xls')
    io = get_io(exp_filename)
    with XlsTemplate(io, properties={'title': 'Title'}) as xls:
        xls.process_model(DemoModel,
                          fields=['id'])

    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_data_default_formats():
    exp_filename = get_target_xls('default_formats.xls')
    io = get_io(exp_filename)
    tz = pytz.timezone('Europe/Rome')

    d = datetime(2014, 3, 7, 3, 59, 0, 0, tzinfo=tz)
    factory(datetime=d,
            date=d.date(),
            time=d.time(),
            option=Option.objects.get_or_create(name='Option 1')[0])

    options ={"default_date_format": 'YYYY MMM DD',
              "default_datetime_format": 'YYYY MM DD hh:mm',
              "default_time_format": 'hh.mm (ss)',
              }
    with XlsTemplate(io, options=options) as xls:
        xls.process_model(DemoModel,
                          fields=['date', 'datetime', 'time'],
                          queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


# @pytest.mark.django_db
# def test_write_enable_vba(data):
#     exp_filename = get_target_xls('test_vba.xls')
#     io = get_io(exp_filename)
#     process_model(DemoModel, io,
#                   exclude=['email'],
#                   options={'vba': True})
#     got, exp = _compare_xlsx_files(io,
#                                    exp_filename)
#
#     assert got == exp
#
