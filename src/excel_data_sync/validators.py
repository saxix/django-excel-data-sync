# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from django.utils.functional import cached_property

logger = logging.getLogger(__name__)

ERROR_TYPE_STOP = "stop"
ERROR_TYPE_WARNING = "warning"
ERROR_TYPE_INFO = "information"
error_types = [ERROR_TYPE_STOP, ERROR_TYPE_WARNING, ERROR_TYPE_INFO]


# validate = ["integer", "decimal", "list", "date", "time", "length", "custom", "any"]
# criteria = {"between": "between",
#             "not between": "not between",
#             "equal to": "==",
#             "not equal to": "!=",
#             "greater than": ">",
#             "less than": "<",
#             "greater than or equal to": ">=",
#             "less than or equal to": "<="
#             }


THIS_COL = 'INDIRECT(ADDRESS(1,COLUMN()) & ":" & ADDRESS(65536, COLUMN()))'
BASE = {"validate": "any",
        "criteria": "",
        "value": 0,
        "maximum": None,
        "ignore_blank": True,
        "dropdown": False,
        "input_title": "",
        "input_message": "",
        "show_input": False,
        "error_title": "Error",
        "error_message": "Invalid input",
        "error_type": ERROR_TYPE_STOP,
        "show_error": True}


class Rule(object):
    def __init__(self, parts=None, error="", message="", is_vba=False):
        self.name = None
        self.formulas = parts or []
        self.error = error
        self.message = message
        self.is_vba = is_vba
        super(Rule, self).__init__()

    def __eq__(self, other):
        return other.name == self.name


class Registry(object):
    __FORMULAS = {
        "any": [],
        # "unique": Rule(['COUNTIF(INDIRECT(ADDRESS(1,COLUMN()) & ":" & ADDRESS(65536, COLUMN())),THIS)=1']),
        "unique": Rule(['COUNTIF({current_column},THIS)=1'],
                       "No duplicates allowed in this column"),
        "number": Rule(['ISNUMBER(VALUE(THIS))'],
                       "Enter a value between {min_value} and {max_value}"),
        "date": Rule(['ISDATE(VALUE(THIS))']),
        "email": Rule(['SEARCH(".",THIS,(SEARCH("@",THIS,1))+2)'],
                      "Not valid email address"),
        "ip": Rule(['(LEN(THIS)-LEN(SUBSTITUTE(THIS,".","")))=3',
                    'ISNUMBER(SUBSTITUTE(THIS,".","")+0)'],
                   "Not a valid IP address"),
        "range": Rule(["VALUE(THIS)>={min_value}", "VALUE(THIS)<={max_value}"],
                      "Enter a value between {min_value} and {max_value}"),
        "max": Rule(["VALUE(THIS)<={max_value}"],
                    "Enter a value between {min_value} and {max_value}"),
        "min": Rule(["VALUE(THIS)>={min_value}"],
                    "Enter a value between {min_value} and {max_value}"),
        "max_length": Rule(["LEN(THIS)<={max_length}"],
                           "String length must be lower than {max_length} chars"),
        "min_length": Rule(["LEN(THIS)>={min_length}"],
                           "String length must be higher than {max_length} chars")
    }

    def __getitem__(self, item):
        return self.__FORMULAS[item]

    def register(self, name, rule, overwrite=False):
        if not isinstance(rule, Rule):
            raise ValueError("not a Rule instance")

        if name in self.__FORMULAS and not overwrite:
            raise ValueError("{} ".format(name))
        rule.name = name
        self.__FORMULAS[name] = rule

        return rule


class RuleEngine(list):
    def __init__(self, iterable=None):
        iterable = iterable or []
        super(RuleEngine, self).__init__(iterable)

    @cached_property
    def rules(self):
        return [registry[y] for y in self]

    def get_rule(self, context):
        ret = []
        for x in self.rules:
            for r in x.formulas:
                f = r.format(**context)
                if f not in ret:
                    ret.append(f)
        return ret

    def get_messages(self, context):
        ret = []
        for x in self.rules:
            msg = x.error.format(**context)
            if msg not in ret:
                ret.append(msg)
        return ret


registry = Registry()
