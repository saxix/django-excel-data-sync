# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging
from datetime import datetime

import pytest
import pytz
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import DateField, DateTimeField, TimeField
from example.management.demo import factory
from example.models import DemoModel, Option
from excel_data_sync.columns import get_column
from excel_data_sync.xls import XlsTemplate
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

# from xlrd import xldate_as_tuple

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("field", [DateField, DateTimeField, TimeField])
def test_validator_date_base(field):
    f = field()
    c = get_column(f)
    c.book = XlsTemplate()
    v = c._get_validation()
    assert v['validate'] == c.validate
    assert v['criteria'] == '>='
    assert v['value'] == datetime(1900, 1, 1, 0, 0, 0, 0)


@pytest.mark.django_db
def test_validator_date_min():
    limits = datetime(2000, 1, 1).date(), datetime(2000, 12, 31).date()
    f = DateField(validators=[MinValueValidator(limits[0])])
    v = get_column(f)._get_validation()
    assert v['validate'] == 'date'
    assert v['criteria'] == '>='
    assert v['value'] == limits[0]


@pytest.mark.django_db
def test_validator_date_max():
    limits = datetime(2000, 1, 1).date(), datetime(2000, 12, 31).date()
    f = DateField(validators=[MaxValueValidator(limits[0])])
    v = get_column(f)._get_validation()
    assert v['validate'] == 'date'
    assert v['criteria'] == '<='
    assert v['value'] == limits[0]


@pytest.mark.django_db
def test_validator_date_range():
    limits = datetime(2000, 1, 1).date(), datetime(2000, 12, 31).date()
    f = DateField(validators=[MinValueValidator(limits[0]),
                              MaxValueValidator(limits[1])])
    v = get_column(f)._get_validation()
    assert v['validate'] == 'date'
    assert v['criteria'] == 'between'
    assert v['value'] == limits[0]
    assert v['maximum'] == limits[1]

    f = DateField()
    v = get_column(f)._get_validation()
    assert v['validate'] == 'date'
    assert v['criteria'] == '>='
    assert v['value'] == datetime(1900, 1, 1, 0, 0)
    # assert v["error_message"] == "Enter a value between {} and {}".format(*limits)
    # assert v['value'] == '=AND(ISDATE(VALUE(THIS)),VALUE(THIS)>={},VALUE(THIS)<={})'.format(*limits)

    # factory()
    # exp_filename = get_target_xls('cols/date_max_min.xls')
    # io = get_io(exp_filename)
    # with XlsTemplate(io) as xls:
    #     xls.process_model(DemoModel,
    #                       fields=['date_range'],
    #                       queryset=DemoModel.objects.all())

    # col = xls.worksheets()[0].columns[0]
    # v = col._get_validation()
    # assert v == {u'value': datetime.datetime(1900, 1, 1, 0, 0), u'validate': u'date', u'criteria': u'>='}
    # FIXME: remove this line
    # import pdb; pdb.set_trace()
    #
    # got, exp = _compare_xlsx_files(io, exp_filename)
    # assert got == exp


@pytest.mark.parametrize("field", ["datetime", "date"])
@pytest.mark.django_db
def test_write_xls(field):
    tz = pytz.timezone('UTC')
    factory(datetime=datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=tz),
            date=datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=tz).date(),
            option=Option.objects.get_or_create(name='Option 1')[0])

    exp_filename = get_target_xls('cols/{}.xls'.format(field))
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel,
                          fields=[field],
                          queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp, "{} does not match".format(exp_filename)


# @pytest.mark.parametrize("field", ["datetime", "date"])
@pytest.mark.django_db
def test_write_timezone():
    tz = pytz.timezone('Europe/Rome')
    d = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=tz)

    factory(datetime=d,
            date=d.date(),
            option=Option.objects.get_or_create(name='Option 1')[0])

    exp_filename = get_target_xls('cols/dates_tz.xls')
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel,
                          fields=['date', 'datetime'],
                          queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp

    from xlrd import open_workbook, xldate_as_tuple
    wb = open_workbook(exp_filename)

    sheet = wb.sheets()[0]
    assert sheet.nrows == 2
    assert sheet.ncols == 2

    cell_value = xldate_as_tuple(sheet.cell(1, 0).value, wb.datemode)
    assert datetime(*cell_value) == d.replace(tzinfo=None)

    cell_value = xldate_as_tuple(sheet.cell(1, 1).value, wb.datemode)
    expected = d.astimezone(pytz.utc).replace(tzinfo=None)
    assert datetime(*cell_value) == expected
