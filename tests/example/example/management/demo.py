# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import itertools
import logging
from datetime import datetime
from decimal import Decimal

import pytz
from django.contrib.auth.models import User
from example.models import DemoModel, Option

# import random


# from faker import Faker

# fake = Faker()

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


# ip = itertools.cycle([fake.ipv6(), '72.223.176.99'])
# value_10 = itertools.cycle(range(9))
# null_logic = itertools.cycle([None, True, False])
# option = itertools.cycle(range(1,9))
# dec = itertools.cycle([Decimal("100.23")])
# fl = itertools.cycle([100.23, 23,32])
# range_5_10 = itertools.cycle([5, 6, 7, 8, 9, 10])
# t = itertools.cycle(["08:00", "09:00"])
#
HOUR = 3600
DAY = HOUR * 24


def factory(r=1, **values):
    if r > len(DemoModel.CHOICES):
        c = 0
    else:
        c = r

    defaults = {
        'big_integer': r,
        'char': 'Name {}'.format(r),
        'choices': DemoModel.CHOICES[c-1][0],
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
        'option': Option.objects.filter(pk=1).first(),
        'positive_integer': '{}'.format(r),
        'positive_small_integer': '{}'.format(r),
        'range_5_10': 5,
        'small_integer': '{}'.format(r),
        'text': 'a' * r,
        'time': datetime.fromtimestamp(r * HOUR).time(),
        'unique': r,
        'url': 'http://nowhere.com/{}'.format(r),
        'uuid': '808506faa4174559a9ecba34ba3decef',
    }
    defaults.update(values)
    if not defaults['option']:
        defaults['option'] = Option.objects.get_or_create(name="Option 1")[0]
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
