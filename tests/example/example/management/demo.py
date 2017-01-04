# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import itertools
from datetime import datetime
from decimal import Decimal

import pytz
from django.contrib.auth.models import User
from example.models import DemoModel, Option


logger = logging.getLogger(__name__)


def create_admin():
    u, created = User.objects.get_or_create(username='admin',
                                            defaults={'is_staff': True,
                                                      'email': 'admin@nowhere.com',
                                                      'is_superuser': True})
    if not created:
        u.is_staff = True
        u.is_superuser = True
    u.set_password('123')
    u.save()

range_5_10 = itertools.cycle([5, 6, 7, 8, 9, 10])
choices = itertools.cycle([1,2,3])

HOUR = 3600
DAY = HOUR * 24


def factory(r=1, **values):
    global range_5_10, choices

    if (r % len(DemoModel.CHOICES)) == 0:
        choices = itertools.cycle([1,2,3])

    if r % 5 == 0:
        range_5_10 = itertools.cycle([5, 6, 7, 8, 9, 10])

    defaults = {
        'big_integer': r,
        'char': 'Name {}'.format(r),
        'choices': next(choices),
        'date': datetime.fromtimestamp((r - 1) * DAY, tz=pytz.UTC).date(),
        'datetime': datetime.fromtimestamp(r * DAY, tz=pytz.UTC),
        'date_range': datetime(2000, 1, 1).date(),
        'decimal': Decimal(r),
        'email': '{}@email.com'.format(r),
        'float': 0.1 * r,
        'generic_ip': "10.10.10.{}".format(r),
        'integer': r * 100,
        'boolean': [True, False][int(r % 2)],
        'max_value_10': 8,
        'null_boolean': [True, False][int(r % 2)],
        'positive_integer': '{}'.format(r),
        'positive_small_integer': '{}'.format(r),
        'range_5_10': next(range_5_10),
        'small_integer': '{}'.format(r),
        'text': 'a' * r,
        'time': datetime.fromtimestamp(r * HOUR).time(),
        'unique': r,
        'url': 'http://nowhere.com/{}'.format(r),
        'uuid': '808506faa4174559a9ecba34ba3decef',
    }
    defaults.update(values)
    if 'option' not in defaults:
        defaults['option'] = Option.objects.get_or_create(name="Option {}".format(r))[0]
    try:
        m = DemoModel.objects.get(id=r)
    except DemoModel.DoesNotExist:
        m = DemoModel(id=r, **defaults)
        m.full_clean()
        m.save()
    return m


def create_sample_data(rows):
    for r in range(10):
        Option.objects.get_or_create(name='Option {}'.format(r))

    for r in range(1, rows + 1):
        factory(r)
