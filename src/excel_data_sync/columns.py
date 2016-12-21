# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import datetime
from django.core import validators
from django.db import models
from django.db.backends.base.operations import BaseDatabaseOperations

from excel_data_sync.validators import RuleEngine, THIS_COL

logger = logging.getLogger(__name__)

fmts = [
    'general',
    '0',
    '0.00',
    '#,##0',
    '#,##0.00',
    '"$"#,##0_);("$"#,##',
    '"$"#,##0_);[Red]("$"#,##',
    '"$"#,##0.00_);("$"#,##',
    '"$"#,##0.00_);[Red]("$"#,##',
    '0%',
    '0.00%',
    '0.00E+00',
    '# ?/?',
    '# ??/??',
    'M/D/YY',
    'D-MMM-YY',
    'D-MMM',
    'MMM-YY',
    'h:mm AM/PM',
    'h:mm:ss AM/PM',
    'h:mm',
    'h:mm:ss',
    'M/D/YY h:mm',
    '_(#,##0_);(#,##0)',
    '_(#,##0_);[Red](#,##0)',
    '_(#,##0.00_);(#,##0.00)',
    '_(#,##0.00_);[Red](#,##0.00)',
    '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)',
    '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)',
    '_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)',
    '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)',
    'mm:ss',
    '[h]:mm:ss',
    'mm:ss.0',
    '##0.0E+0',
    '@'
]


# xls_options_default = {
# 'date_format': 'd/m/Y',
#                        'datetime_format': 'N j, Y, P',
#                        'time_format': 'P',
#                        'sheet_name': 'Sheet1',
# models.DateField: 'DD MMM-YY',
# models.DateTimeField: 'DD MMD YY hh:mm',
# models.TimeField: 'hh:mm',
# models.IntegerField: '#,##',
# models.PositiveIntegerField: '#,##',
# models.PositiveSmallIntegerField: '#,##',
# models.BigIntegerField: '#,##',
# models.DecimalField: '#,##0.00',
# models.BooleanField: 'boolean',
# models.NullBooleanField: 'boolean',
# models.EmailField: lambda value: 'HYPERLINK("mailto:%s","%s")' % (value, value),
# models.URLField: lambda value: 'HYPERLINK("%s","%s")' % (value, value),
# models.CurrencyColumn': '"$"#,##0.00);[Red]("$"#,##0.00)',
# }


# class Format(dict):
#     def __repr__(self):
#         return ";".join(["{}:{}".format(k, v) for k, v in self.items()])


class Header(object):
    format = {'bold': True,
              'locked': 1,
              'align': 'center',
              'num_format': ''}
    num_format = ''

    def __init__(self, column):
        self.column = column
        self.title = column.verbose_name.title()

    def get_format(self, book):
        fmt = dict(self.format)
        fmt['num_format'] = self.num_format
        return book.add_format(fmt)


class Column(object):
    max_value = None
    min_value = None
    max_length = None
    format = {'locked': 0}
    num_format = ''
    main_validator = None
    validate = 'custom'

    # worksheet.data_validation('B25', {'validate': 'integer',

    def __init__(self, field, options=None):
        self.field = field
        self.options = options or {}
        self.field_type = type(field)
        self.rule_parser = RuleEngine(self.main_validator)
        self.default = field.default
        self.max_length = field.max_length

    def get_value_from_object(self, record):
        return getattr(record, self.field.name)

    def get_format(self, book):
        fmt = dict(self.format)
        fmt['num_format'] = self.num_format
        return book.add_format(fmt)

    def parse_validators(self):
        for validator in self.field.validators:
            if isinstance(validator, validators.MaxLengthValidator):
                self.max_length = validator.limit_value
                self.rule_parser.append("max_length")
            elif isinstance(validator, validators.MaxValueValidator):
                self.max_value = validator.limit_value
                self.rule_parser.append("max")
            elif isinstance(validator, validators.MinValueValidator):
                self.min_value = validator.limit_value
                self.rule_parser.append("min")

    def process_workbook(self, book, sheet):
        sheet.data_validation(1, self.number,
                              65000, self.number,
                              self._get_validation())

    def _get_validation(self):
        try:
            if self.field.unique:
                self.rule_parser.append("unique")
            if self.field.choices:
                return {"validate": "list",
                        "dropdown": True,
                        "value": [x[1] for x in self.field.choices]}
            if self.max_length is not None:
                self.rule_parser.append("max_length")
            self.parse_validators()
            context = dict(current_column=THIS_COL,
                           max_value=self.max_value,
                           min_value=self.min_value,
                           max_length=self.max_length)
            if self.rule_parser:
                formula = "=AND(%s)" % ",".join(self.rule_parser.get_rule(context))
            else:
                return {"validate": "any"}

            return {"validate": "custom",
                    "criteria": "",
                    "value": formula,
                    "error_message": "\n".join(self.rule_parser.get_messages(context)),
                    # "error_message": "Enter a value between {} and {}".format(self.min_value,
                    #                                                           self.max_value),
                    }
        except Exception as e:  # pragma: no-cover
            logger.exception(e)
            return {"validate": "any"}

    def __getattr__(self, item):
        if item in ('blank', 'null', 'max_length', 'name', 'related_model',
                    'choices', 'unique', 'verbose_name',):
            return getattr(self.field, item)
        raise AttributeError(item)  # pragma: no-cover

    def __repr__(self):
        return """<Column {0.verbose_name}
{0.blank}
{0.null}
{0.max_length}>""".format(self)

    def __str__(self):
        return """<Column {0.verbose_name}>""".format(self)


class DateColumn(Column):
    num_format = 'D MMM YYYY'  # date_time = datetime.datetime.strptime('2013-01-23', '%Y-%m-%d')
    main_validator = ["date"]

    def _get_validation(self):
        return {"validate": "date",
                "criteria": ">=",
                "value": datetime.datetime(1900, 1, 1)}


class DateTimeColumn(DateColumn):
    num_format = 'D MMM YYYY h:mm:ss'  # date_time = datetime.datetime.strptime('2013-01-23', '%Y-%m-%d')

    def get_value_from_object(self, record):
        v = super(DateColumn, self).get_value_from_object(record)
        return v.astimezone(self.options['timezone']).replace(tzinfo=None)


class TimeColumn(DateColumn):
    num_format = 'h:mm:ss'  # date_time = datetime.datetime.strptime('2013-01-23', '%Y-%m-%d')
    main_validator = ["date"]


class NumberColumn(Column):
    num_format = '#,##'
    main_validator = ["number"]

    def __init__(self, field, options=None):
        super(NumberColumn, self).__init__(field, options)
        self.min_value, self.max_value = BaseDatabaseOperations.integer_field_ranges[field.get_internal_type()]


class SmallIntegerColumn(NumberColumn):
    pass


class IntegerColumn(NumberColumn):
    pass


class BigIntegerColumn(NumberColumn):
    pass


class PositiveSmallIntegerColumn(NumberColumn):
    pass


class PositiveIntegerColumn(NumberColumn):
    def __init__(self, field, options=None):
        super(PositiveIntegerColumn, self).__init__(field, options)


class DecimalColumn(Column):
    num_format = '#,##0.00'
    main_validator = ["number"]


class FloatColumn(Column):
    num_format = '#,##0.00'
    main_validator = ["number"]


class BooleanColumn(Column):
    def _get_validation(self):
        return {"validate": "list",
                "dropdown": True,
                "value": ["True", "False"]}


class NullBooleanColumn(Column):
    def _get_validation(self):
        return {"validate": "list",
                "dropdown": True,
                "value": ["", "True", "False"]}


class IpAddressColumn(Column):
    main_validator = ["ip"]


class UUIDColumn(Column):
    num_format = 'general'

    def get_value_from_object(self, record):
        return getattr(record, self.field.name).hex


class TextColumn(Column):
    num_format = 'general'


class EmailColumn(Column):
    main_validator = ["email"]


class ForeignKeyColumn(Column):
    def get_value_from_object(self, record):
        return str(getattr(record, self.field.name))

    def process_workbook(self, book, sheet):
        sheet_name = '{0.app_label}.{0.model_name}'.format(self.field.related_model._meta)
        fksheet = book.add_worksheet(sheet_name)
        fksheet.hide()
        for i, opt in enumerate([[x.pk, str(x)] for x in self.field.rel.model.objects.all()]):
            id, label = opt
            fksheet.write(i, 0, id)
            fksheet.write(i, 1, label)
        sheet.data_validation(1, self.number,
                              65000, self.number,
                              {"validate": "list",
                               "dropdown": True,
                               "value": "=example.option!$B:$B"
                               }
                              )

    def _get_validation(self):
        related = self.field.rel.to
        return {"validate": "list",
                "dropdown": True,
                "value": [str(x) for x in related.objects.all()]}


mapping = {models.SmallIntegerField: SmallIntegerColumn,
           models.IntegerField: IntegerColumn,
           models.BigIntegerField: BigIntegerColumn,
           models.PositiveSmallIntegerField: PositiveSmallIntegerColumn,
           models.PositiveIntegerField: PositiveIntegerColumn,
           models.GenericIPAddressField: IpAddressColumn,

           models.ForeignKey: ForeignKeyColumn,

           models.BooleanField: BooleanColumn,
           models.NullBooleanField: NullBooleanColumn,

           models.DecimalField: DecimalColumn,
           models.FloatField: FloatColumn,

           models.DateField: DateColumn,
           models.DateTimeField: DateTimeColumn,
           models.TimeField: TimeColumn,

           models.EmailField: EmailColumn,
           models.CharField: TextColumn,
           models.TextField: TextColumn,
           models.UUIDField: UUIDColumn,
           models.URLField: TextColumn,
           }


def get_column(field, options=None):
    return mapping.get(type(field), Column)(field, options)
