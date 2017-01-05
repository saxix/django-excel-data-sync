# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
from datetime import datetime

import pytz
from django.db.models import NOT_PROVIDED
from excel_data_sync.columns import Header, get_column
from excel_data_sync.config import config
from xlsxwriter import Workbook
from xlsxwriter.chartsheet import Chartsheet
from xlsxwriter.worksheet import Worksheet

logger = logging.getLogger(__name__)


class XlsRuleSheet(Worksheet):
    is_rule = True
    NULL = 1
    BLANK = 2
    UNIQUE = 3
    REQUIRED = 4
    DEFAULT = 5
    MAX_LENGTH = 6
    PRIMARY_KEY = 7
    EDITABLE = 8
    COLUMN = 9
    RULES = 10

    def _initialize(self, init_data):
        super(XlsRuleSheet, self)._initialize(init_data)
        self.write(self.NULL, 0, 'null')
        self.write(self.BLANK, 0, 'blank')
        self.write(self.REQUIRED, 0, 'required')
        self.write(self.UNIQUE, 0, 'unique')
        self.write(self.DEFAULT, 0, 'default')
        self.write(self.MAX_LENGTH, 0, 'max_length')
        self.write(self.PRIMARY_KEY, 0, 'primary_key')
        self.write(self.EDITABLE, 0, 'editable')
        if self._book.hide:
            self.hide()

    def add_column(self, column):
        self.write(0, column.number + 1, column.header.title)
        self.write_boolean(self.NULL, column.number + 1, column.field.null)
        self.write_boolean(self.BLANK, column.number + 1, column.field.blank)
        self.write_boolean(self.UNIQUE, column.number + 1, column.field.unique)
        if column.field.max_length:
            self.write_number(self.MAX_LENGTH, column.number + 1, column.field.max_length)
        self.write_boolean(self.PRIMARY_KEY, column.number + 1, column.field.max_length)
        self.write_boolean(self.EDITABLE, column.number + 1, column.field.max_length)
        self.write(self.COLUMN, column.number + 1, column.__class__.__name__)

        default = column.field.default
        if not default == NOT_PROVIDED:
            if callable(default):
                value = str(default())
            else:
                value = str(default)
            self.write(self.DEFAULT, column.number + 1, value)


class XlsWorkSheet(Worksheet):
    def __init__(self):
        super(XlsWorkSheet, self).__init__()
        self.columns = []
        self.headers = []

    def protect(self, password='', options=None):
        options = {
            'sheet': False,
            'content': False,
            'objects': False,
            'scenarios': True,
            'format_cells': True,
            'format_columns': True,
            'format_rows': True,
            'insert_columns': False,
            'insert_rows': False,
            'insert_hyperlinks': False,
            'delete_columns': False,
            'delete_rows': False,
            'select_locked_cells': True,
            'sort': True,
            'autofilter': True,
            'pivot_tables': False,
            'select_unlocked_cells': True
        }
        password = password or self._book.password
        return super(XlsWorkSheet, self).protect(password, options)

    def _initialize(self, init_data):
        super(XlsWorkSheet, self)._initialize(init_data)

    def add_column(self, column, header=None):
        column.number = len(self.columns)
        column._sheet = self
        self.columns.append(column)
        if column.need_vba:
            self._book.add_vba()

        if not header:
            header = Header(column)
        self.headers.append(header)
        self.rules.add_column(column)

    def write_columns(self):
        for i, header in enumerate(self.headers):
            column = header.column
            self.write(0, i, header.title, header._get_format())
            help = str(header.column.field.help_text)
            if help:
                self.write_comment(0, i, help)
            column.format_column()
            column.add_data_validation()
            self.rules.write(XlsRuleSheet.RULES,
                             column.number + 1,
                             ",".join(column.rule_parser))


class XlsTemplate(Workbook):
    chartsheet_class = Chartsheet
    worksheet_class = XlsWorkSheet
    header_class = Header

    def __init__(self, filename=None, options=None, properties=None,
                 protect=True, hide=True, header_class=None, password='',
                 **kwargs):
        options = options or {}
        options.setdefault('default_date_format', 'D-MMM-YYYY')
        options.setdefault('default_datetime_format', 'DD MMM YYYY hh:mm')
        options.setdefault('default_time_format', 'hh:mm:ss')
        options.setdefault('strings_to_numbers', True)

        self._vba_added = False
        self.protect = protect
        self.password = password
        self.hide = hide
        self.timezone = options.pop('timezone', pytz.utc)

        self.header_class = header_class or self.header_class

        super(XlsTemplate, self).__init__(filename, options)

        self.default_datetime_format = self.add_format({'locked': False,
                                                        'num_format': options['default_datetime_format']})
        self.default_time_format = self.add_format({'locked': False,
                                                    'num_format': options['default_time_format']})
        self.default_date_format = self.add_format({'locked': False,
                                                    'num_format': options['default_date_format']})

        self.set_custom_property("Creation Date", datetime.today(), "date")

        self.define_name('THIS', '=!A1')
        self.define_name('THIS_COL', '=!A')

        self.set_properties(properties)

    def set_properties(self, custom=None, **kwargs):
        request = kwargs.pop('request', None)
        custom = custom or {}
        args = dict(model=getattr(self, '_model', None),
                    request=request)

        def process(value):
            try:
                if callable(value):
                    return value(**args)
                else:
                    return value.format(**args)
            except Exception as e:
                logger.exception(e)
                return ""

        values = {}
        for key, value in config['properties'].items():
            if key in custom:
                value = custom[key]
            values[key] = process(value)
        self.doc_properties = dict((k, v) for k, v in values.items()
                                   if v or k in ['manager', 'hyperlink_base',
                                                 'title', 'subject',
                                                 'keywords', 'comments',
                                                 'category'])

    def add_vba(self):
        if not self._vba_added:
            self.add_vba_project(os.path.join(os.path.dirname(__file__), 'vbaProject.bin'))
            self._vba_added = True

    def process_model(self, model, fields=None, exclude=None, queryset=None):
        self._model = model
        self.set_custom_property("Model", str(model.__name__))

        sheet = self.add_worksheet(model._meta.model_name)
        meta = model._meta
        if fields is None:
            fields = [field.name for field in meta.get_fields()]
        if exclude is None:
            exclude = []

        for field_name in fields:
            if field_name in exclude:
                continue
            field = meta.get_field(field_name)
            c = get_column(field)
            sheet.add_column(c)

        sheet.write_columns()

        if queryset:
            for row, record in enumerate(queryset, 1):
                for colnum, column in enumerate(sheet.columns):
                    column.write_cell(row, colnum, record)

    def _add_rule_sheet(self, owner):
        rulesheet = XlsRuleSheet()
        sheet_index = len(self.worksheets_objs)
        name = "{}.__rules__".format(owner.name)
        init_data = {
            'name': name,
            'index': sheet_index,
            'str_table': self.str_table,
            'worksheet_meta': self.worksheet_meta,
            'optimization': self.optimization,
            'tmpdir': self.tmpdir,
            'date_1904': self.date_1904,
            'strings_to_numbers': self.strings_to_numbers,
            'strings_to_formulas': self.strings_to_formulas,
            'strings_to_urls': self.strings_to_urls,
            'nan_inf_to_errors': self.nan_inf_to_errors,
            'default_date_format': self.default_date_format,
            'default_url_format': self.default_url_format,
            'excel2003_style': self.excel2003_style,
            'remove_timezone': self.remove_timezone,
        }
        rulesheet._book = self
        rulesheet._initialize(init_data)

        self.worksheets_objs.append(rulesheet)
        self.sheetnames[name] = rulesheet
        owner.rules = rulesheet

    def _add_sheet(self, name, is_chartsheet=None, worksheet_class=None):
        if worksheet_class:
            worksheet = worksheet_class()
        else:
            if is_chartsheet:
                worksheet = self.chartsheet_class()
            else:
                worksheet = self.worksheet_class()

        sheet_index = len(self.worksheets_objs)
        name = self._check_sheetname(name, isinstance(worksheet, Chartsheet))

        # Initialization data to pass to the worksheet.
        init_data = {
            'name': name,
            'index': sheet_index,
            'str_table': self.str_table,
            'worksheet_meta': self.worksheet_meta,
            'optimization': self.optimization,
            'tmpdir': self.tmpdir,
            'date_1904': self.date_1904,
            'strings_to_numbers': self.strings_to_numbers,
            'strings_to_formulas': self.strings_to_formulas,
            'strings_to_urls': self.strings_to_urls,
            'nan_inf_to_errors': self.nan_inf_to_errors,
            'default_date_format': self.default_date_format,
            'default_url_format': self.default_url_format,
            'excel2003_style': self.excel2003_style,
            'remove_timezone': self.remove_timezone,
        }

        worksheet._initialize(init_data)
        worksheet._book = self

        self.worksheets_objs.append(worksheet)
        self.sheetnames[name] = worksheet
        self._add_rule_sheet(worksheet)

        if self.protect:
            worksheet.protect()

        return worksheet

    def __del__(self):
        """Close file in destructor if it hasn't been closed explicitly."""
        try:
            if not self.fileclosed and self.filename:
                self.close()
        except:  # pragma: no cover
            raise Exception("Exception caught in workbook destructor. "
                            "Explicit close() may be required for workbook.")
