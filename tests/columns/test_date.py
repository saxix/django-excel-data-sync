# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import datetime
import logging

import pytest
import pytz
from django.db.models import DateField, DateTimeField, TimeField

from example.management.demo import factory
from example.models import Option, DemoModel
from excel_data_sync.columns import get_column
from excel_data_sync.inspector import process_model
from excel_data_sync.xls import XlsTemplate
from helperfunctions import get_target_xls, _compare_xlsx_files, get_io

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("field", [DateField, DateTimeField, TimeField])
def test_validator_date_base(field):
    f = field()
    c = get_column(f)
    c.book = XlsTemplate()
    v = c._get_validation()
    assert v['validate'] == 'date'
    assert v['criteria'] == '>='
    assert v['value'] == datetime.datetime(1900, 1, 1, 0, 0, 0, 0)


@pytest.mark.parametrize("field", ["datetime"])
@pytest.mark.django_db
def test_write_xls(field):
    # tz = pytz.timezone('Europe/Rome')
    tz = pytz.timezone('UTC')
    r = factory(datetime=datetime.datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=tz),
                option=Option.objects.get_or_create(name='Option 1')[0])

    exp_filename = get_target_xls('cols/{}.xls'.format(field))
    io = get_io(exp_filename)
    process_model(DemoModel, io,
                  fields=[field],
                  queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
