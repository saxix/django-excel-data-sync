# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import logging
from six import python_2_unicode_compatible

from django.core import validators
from django.db import models
from django.db.backends.base.operations import BaseDatabaseOperations
from django.utils.encoding import smart_str
from excel_data_sync.validators import THIS_COL, RuleEngine
from xlsxwriter.worksheet import convert_cell_args

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


@python_2_unicode_compatible
class Header(object):
    format = {'bold': True,
              'locked': 1,
              'align': 'center',
              'num_format': ''}
    num_format = ''

    def __init__(self, column):
        self.column = column
        self.title = column.verbose_name.title()

    def __str__(self):
        return smart_str("<Header {0.column.verbose_name}>".format(self))

    def get_format(self):
        fmt = dict(self.format)
        fmt['num_format'] = self.num_format
        return self.column._sheet._book.add_format(fmt)


@python_2_unicode_compatible
class Column(object):
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
        self.max_value = None
        self.min_value = None

    @convert_cell_args
    def write_cell(self, row, col, record, *args):
        v = self._get_value_from_object(record)
        self._sheet.write(row, col, v, self.get_format())

    @convert_cell_args
    def format_column(self):
        self._sheet.set_column(self.number,
                               self.number, cell_format=self.get_format())

        # self._sheet.write_blank(row, col, '', self.get_format(self._sheet._book))

    def _get_value_from_object(self, record):
        if self.field.choices:
            getter = 'get_{}_display'.format(self.field.name)
            return getattr(record, getter)()
        return getattr(record, self.field.name)

    def to_xls(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        return value

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        return value

    def get_format(self):
        fmt = dict(self.format)
        fmt['num_format'] = self.num_format
        return self._sheet._book.add_format(fmt)

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

    def process_workbook(self):
        self._sheet.data_validation(1, self.number,
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
        return smart_str("<{0.__class__.__name__} '{0.verbose_name}'>".format(self))

    def __str__(self):
        return """<Column {0.verbose_name}>""".format(self)


class DateColumn(Column):
    format = {'locked': 0, }
    # num_format = 'D MMM YYYY'  # date_time = datetime.datetime.strptime('2013-01-23', '%Y-%m-%d')
    main_validator = ["date"]
    _format_attr = 'default_date_format'

    def get_format(self):
        return getattr(self._sheet._book, self._format_attr)

    @convert_cell_args
    def write_cell(self, row, col, record, *args):
        v = self._get_value_from_object(record)
        self._sheet.write_datetime(row, col, v, self.get_format())

    def _get_validation(self):
        self.parse_validators()
        value = datetime.datetime(1900, 1, 1)
        criteria = ">="
        maximum = None
        if self.rule_parser:
            if "min" in self.rule_parser and "max" in self.rule_parser:
                criteria = "between"
                value = self.min_value
                maximum = self.max_value
            elif "min" in self.rule_parser:
                criteria = ">="
                value = self.min_value
            elif "max" in self.rule_parser:
                criteria = "<="
                value = self.max_value

        return {"validate": "date",
                "criteria": criteria,
                "value": value,
                "maximum": maximum}


class DateTimeColumn(DateColumn):
    # num_format = 'D MMM YYYY h:mm:ss'  # date_time = datetime.datetime.strptime('2013-01-23', '%Y-%m-%d')
    _format_attr = 'default_datetime_format'

    def _get_value_from_object(self, record):
        v = super(DateColumn, self)._get_value_from_object(record)
        return v.astimezone(self._sheet._book.timezone).replace(tzinfo=None)


class TimeColumn(DateColumn):
    # num_format = 'h:mm:ss'  # date_time = datetime.datetime.strptime('2013-01-23', '%Y-%m-%d')
    _format_attr = 'default_time_format'
    main_validator = ["date"]


class NumberColumn(Column):
    num_format = '#,##'
    main_validator = ["number"]

    def __init__(self, field, options=None):
        super(NumberColumn, self).__init__(field, options)
        self.min_value, self.max_value = BaseDatabaseOperations.integer_field_ranges[field.get_internal_type()]

    def parse_validators(self):
        super(NumberColumn, self).parse_validators()
        self.rule_parser.append("min")
        self.rule_parser.append("max")


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


class AutoColumn(NumberColumn):
    as_internal_type = "IntegerField"

    def __init__(self, field, options=None):
        super(NumberColumn, self).__init__(field, options)
        self.min_value, self.max_value = BaseDatabaseOperations.integer_field_ranges[self.as_internal_type]


class BigAutoColumn(AutoColumn):
    as_internal_type = "BigIntegerField"


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

    def _get_value_from_object(self, record):
        return getattr(record, self.field.name).hex


class TextColumn(Column):
    num_format = 'general'


class EmailColumn(Column):
    main_validator = ["email"]


class ForeignKeyColumn(Column):
    def _get_value_from_object(self, record):
        return str(getattr(record, self.field.name))

    def process_workbook(self):
        sheet_name = '{0.app_label}.{0.model_name}'.format(self.field.related_model._meta)
        fksheet = self._sheet._book.add_worksheet(sheet_name)
        fksheet.hide()
        for i, opt in enumerate([[x.pk, str(x)] for x in self.field.rel.model.objects.all()]):
            id, label = opt
            fksheet.write(i, 0, id)
            fksheet.write(i, 1, label)
        self._sheet.data_validation(1, self.number,
                                    65000, self.number,
                                    {"validate": "list",
                                     "dropdown": True,
                                     "value": "=example.option!$B:$B"
                                     }
                                    )

    def _get_validation(self):
        return {}


mapping = {models.Field: Column,
           models.SmallIntegerField: SmallIntegerColumn,
           models.IntegerField: IntegerColumn,
           models.BigIntegerField: BigIntegerColumn,
           models.PositiveSmallIntegerField: PositiveSmallIntegerColumn,
           models.PositiveIntegerField: PositiveIntegerColumn,
           models.GenericIPAddressField: IpAddressColumn,

           models.AutoField: AutoColumn,
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

try:
    mapping[models.BigAutoField] = BigAutoColumn
except AttributeError:
    pass


def register_column(key, col):
    if isinstance(key, models.Field):
        target = "{}.{}.{}".format(key.model._meta.app_label,
                                   key.model._meta.model_name,
                                   key.name).lower()
    else:
        target = key
    mapping[target] = col


def unregister_column(key):
    if isinstance(key, models.Field):
        target = "{}.{}.{}".format(key.model._meta.app_label,
                                   key.model._meta.model_name,
                                   key.name).lower()
    else:
        target = key
    del mapping[target]


def get_column(field, options=None):
    try:
        target = "{}.{}.{}".format(field.model._meta.app_label,
                                   field.model._meta.model_name,
                                   field.name).lower()
        klass = mapping.get(target, mapping.get(type(field), Column))
    except AttributeError:
        klass = mapping.get(type(field), Column)
    try:
        return klass(field, options)
    except TypeError:  # pragma: no cover
        raise ValueError("unknown field {}".format(field))
