# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULTS = {'properties': {"title": "Project2 a {model._meta.verbose_name} data entry",
                           "author": "{request.user.username}",
                           'subject': '',
                           'status': '',
                           'manager': '',
                           'company': '',
                           'category': '',
                           'keywords': '',
                           'comments': '',
                           'hyperlink_base': '',
                           }
            }

config = getattr(settings, 'XLS_DATASYNC', {})

for key in (DEFAULTS.keys()):
    config[key] = DEFAULTS[key]
