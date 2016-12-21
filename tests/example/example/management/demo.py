# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
# import random

import itertools

from decimal import Decimal
from datetime import datetime
from django.contrib.auth.models import User
from example.models import DemoModel, Option
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


choices = itertools.cycle(DemoModel.CHOICES)


# ip = itertools.cycle([fake.ipv6(), '72.223.176.99'])
# value_10 = itertools.cycle(range(9))
# null_logic = itertools.cycle([None, True, False])
# option = itertools.cycle(range(1,9))
# dec = itertools.cycle([Decimal("100.23")])
# fl = itertools.cycle([100.23, 23,32])
# range_5_10 = itertools.cycle([5, 6, 7, 8, 9, 10])
# t = itertools.cycle(["08:00", "09:00"])
#

def factory(r=1, **values):
    # seed = values.pop('seed', None)
    # fake.seed(seed)
    # random.seed(seed)

    defaults = {
        'bigint': r,
        'char': 'Name {}'.format(r),
        'choices': next(choices)[0],
        'date': datetime.fromtimestamp(r * 1000000).date(),
        'datetime': datetime.fromtimestamp(r * 1000000),
        'decimal': Decimal(r),
        'email': '{}@email.com'.format(r),
        'float': 0.1 * r,
        'generic_ip': "10.10.10.{}".format(r),
        'integer': r * 100,
        'logic': [True, False][int(r % 2)],
        'max_value_10': 8,
        'null_logic': [True, False][int(r % 2)],
        'option': Option.objects.filter(pk=1).first(),
        'positive_integer': '{}'.format(r),
        'positive_small_integer': '{}'.format(r),
        'range_5_10': 5,
        'small_integer': '{}'.format(r),
        'text': 'a' * r,
        'time': datetime.fromtimestamp(r * 1000000).time(),
        'unique': r,
        'url': 'http://nowhere.com/{}'.format(r),
        'uuid': '808506faa4174559a9ecba34ba3decef',
    }
    defaults.update(values)
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
