# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging

from django.db.models import BooleanField, NullBooleanField
from excel_data_sync.columns import get_column

logger = logging.getLogger(__name__)


def test_validator_booleanfield():
    c = get_column(BooleanField())
    v = c._get_validation()
    assert v['validate'] == 'list'
    assert v['value'] == ["True", "False"]


def test_validator_nullbooleanfield():
    c = get_column(NullBooleanField())
    v = c._get_validation()
    assert v['validate'] == 'list'
    assert v['value'] == ["", "True", "False"]
