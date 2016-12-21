# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging

from django.db.models import UUIDField
from excel_data_sync.columns import get_column, UUIDColumn

logger = logging.getLogger(__name__)


def test_validation():
    f = UUIDField('Field1')
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'custom'


def test_validator_uuidfield():
    f = UUIDField()
    c = get_column(f)
    v = c._get_validation()
    assert isinstance(c, UUIDColumn)
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(LEN(THIS)<={})'.format(f.max_length)
    assert v["error_message"] == "String length must be lower than {} chars".format(f.max_length)
