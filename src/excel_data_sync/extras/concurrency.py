# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from concurrency.fields import IntegerVersionField, AutoIncVersionField, TriggerVersionField
from django.db.backends.base.operations import BaseDatabaseOperations

from excel_data_sync.columns import register_column, NumberColumn

logger = logging.getLogger(__name__)


class ConcurrencyColumn(NumberColumn):
    format = {'locked': 1}
    num_format = '#'
    main_validator = ["number"]

    def __init__(self, field, options=None):
        super(NumberColumn, self).__init__(field, options)
        self.min_value, self.max_value = BaseDatabaseOperations.integer_field_ranges["BigIntegerField"]

    def get_format(self):
        fmt = dict(self.format)
        fmt['num_format'] = self.num_format
        return self._sheet._book.add_format(fmt)


register_column(IntegerVersionField, ConcurrencyColumn)
register_column(AutoIncVersionField, ConcurrencyColumn)
register_column(TriggerVersionField, ConcurrencyColumn)
