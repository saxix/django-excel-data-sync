# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytz

from excel_data_sync.columns import get_column, Header
from excel_data_sync.xls import XlsTemplate

logger = logging.getLogger(__name__)


def inspect(model, global_options=None, fields=None, exclude=None):
    meta = model._meta
    columns = []
    if exclude is None:
        exclude = []
    colnum = 0
    for field in meta.get_fields():
        if field.name in exclude:
            continue
        if fields and field.name not in fields:
            continue
        c = get_column(field, global_options)
        c.number = colnum
        columns.append(c)
        colnum += 1

    headers = [Header(col) for col in columns]

    return columns, headers


def process_model(model, filename=None, fields=None, exclude=None,
                  queryset=None,
                  options=None, properties=None):
    with XlsTemplate(filename, options=options, properties=properties) as book:
        sheet = book.add_worksheet(model._meta.model_name)

        columns, headers = inspect(model, {'show_input': True,
                                           'timezone': pytz.UTC},
                                   fields=fields, exclude=exclude)

        for i, header in enumerate(headers):
            sheet.write(0, i, header.title, header.get_format(book))

        for i, col in enumerate(columns):
            col.process_workbook(book, sheet)
            # sheet.data_validation(1, i, 65000, i, col.get_validation())

        if queryset:
            for row, record in enumerate(queryset, 1):
                for colnum, column in enumerate(columns):
                    v = column.get_value_from_object(record)
                    sheet.write(row, colnum, v, column.get_format(book))
    return book
