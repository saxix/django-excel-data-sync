# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

logger = logging.getLogger(__name__)

FACTORIES = {'now': '=NOW()',
             'today': '=TODAY()',
             'uuid': '=CONCATENATE(DEC2HEX(RANDBETWEEN(0;4294967295);8);'
                     'DEC2HEX(RANDBETWEEN(0;42949);4);'
                     'DEC2HEX(RANDBETWEEN(0;42949);4);'
                     'DEC2HEX(RANDBETWEEN(0;42949);4);'
                     'DEC2HEX(RANDBETWEEN(0;4294967295);8);'
                     'DEC2HEX(RANDBETWEEN(0;42949);4))',

             }
