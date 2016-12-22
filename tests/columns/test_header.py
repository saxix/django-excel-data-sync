# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from six import StringIO

import xlsxwriter
from django.db.models import IntegerField
from excel_data_sync.columns import Column, Header

logger = logging.getLogger(__name__)


def test_base():
    f = IntegerField('Field1')
    c = Column(f)
    h = Header(c)
    book = xlsxwriter.Workbook(StringIO())

    assert h.get_format(book).num_format == ''
