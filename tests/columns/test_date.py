# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import datetime
import logging

import pytest
from django.db.models import DateField, DateTimeField, TimeField
from excel_data_sync.columns import get_column

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("field", [DateField, DateTimeField, TimeField])
def test_validator_text_base(field):
    f = field()
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'date'
    assert v['criteria'] == '>='
    assert v['value'] == datetime.datetime(1900, 1, 1, 0, 0)
