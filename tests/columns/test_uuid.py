# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

import logging

from django.db.models import UUIDField
from excel_data_sync.columns import UUIDColumn, get_column

logger = logging.getLogger(__name__)


def test_validation():
    f = UUIDField('Field1')
    c = get_column(f)
    v = c._get_validation()
    assert v['validate'] == 'custom'


def test_validator_uuidfield():
    f = UUIDField(blank=True)
    c = get_column(f)
    v = c._get_validation()
    assert isinstance(c, UUIDColumn)
    assert c.rule_parser == ['uuid', 'length']
    assert v['validate'] == 'custom'
    assert v['value'] == '=AND(HEX2DEC(THIS),LEN(THIS)=32)'
    assert v["error_message"] == """It is not a valid UUID
String length must be exactly 32 chars"""
