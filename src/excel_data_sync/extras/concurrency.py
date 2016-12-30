# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from concurrency.fields import IntegerVersionField, AutoIncVersionField, TriggerVersionField
from django.db.backends.base.operations import BaseDatabaseOperations
from xlsxwriter.worksheet import convert_cell_args

from excel_data_sync.columns import register_column, NumberColumn

logger = logging.getLogger(__name__)


class ConcurrencyColumn(NumberColumn):
    num_format = '#'
    main_validator = ["number"]

    def __init__(self, field, options=None):
        super(NumberColumn, self).__init__(field, options)
        self.min_value, self.max_value = BaseDatabaseOperations.integer_field_ranges["BigIntegerField"]

    @convert_cell_args
    def write_cell(self, row, col, record, *args):
        v = self._get_value_from_object(record)
        self._sheet.write(row, col, v, self.get_format(locked=1))


register_column(IntegerVersionField, ConcurrencyColumn)
register_column(AutoIncVersionField, ConcurrencyColumn)
register_column(TriggerVersionField, ConcurrencyColumn)
