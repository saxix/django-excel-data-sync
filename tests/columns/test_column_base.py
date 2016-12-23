# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from six import BytesIO as StringIO

from django.db.models import Field, IntegerField, CharField, PositiveSmallIntegerField
from excel_data_sync.columns import IntegerColumn, get_column
from excel_data_sync.xls import XlsTemplate

logger = logging.getLogger(__name__)


def test_base():
    f = IntegerField('Field1')
    c = get_column(f)
    assert c.blank == f.blank
    assert c.null == f.null
    assert c.max_length == f.max_length
    assert c.choices == f.choices


def test_repr():
    f = IntegerField('Field1')
    c = get_column(f)

    assert str(c) == "<Column Field1>"
    assert repr(c) == """<Column Field1
False
False
None>"""


def test_get_column():
    f = IntegerField('Field1')
    c = get_column(f)
    assert isinstance(c, IntegerColumn)


def test_validation():
    f = Field('Field1')
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'any'
    # assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)))'
    # assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)))'


def test_format():
    with XlsTemplate(StringIO()) as book:
        f = IntegerField('Field1')
        c = get_column(f)
        assert c.get_format(book).num_format == c.num_format


def test_unique():
    f = PositiveSmallIntegerField('Field1', unique=True)
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(ISNUMBER(VALUE(THIS)),' \
                         'COUNTIF(INDIRECT(ADDRESS(1,COLUMN()) & ":" & ADDRESS(65536, COLUMN())),THIS)=1,' \
                         'VALUE(THIS)>=0,VALUE(THIS)<=32767)'
    assert v["error_message"].split("\n")[1] == "No duplicates allowed in this column"


def test_choices():
    f = IntegerField("Field1", choices=((1, "Opt1"), (2, "Opt2")))
    v = get_column(f)._get_validation()
    assert v['validate'] == 'list'
    assert v['value'] == ["Opt1", "Opt2"]
