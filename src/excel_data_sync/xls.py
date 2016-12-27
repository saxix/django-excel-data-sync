# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from warnings import warn

import pytz
from excel_data_sync.columns import Header, get_column
from xlsxwriter import Workbook
from xlsxwriter.chartsheet import Chartsheet
from xlsxwriter.compatibility import force_unicode
from xlsxwriter.utility import supported_datetime
from xlsxwriter.worksheet import Worksheet, convert_range_args

logger = logging.getLogger(__name__)


class XlsWorkSheet(Worksheet):
    def __init__(self):
        super(XlsWorkSheet, self).__init__()
        self.columns = []
        self.headers = []

    def add_column(self, column, header=None):
        column.number = len(self.columns)
        column._sheet = self
        self.columns.append(column)
        if not header:
            header = Header(column)
        self.headers.append(header)

    @convert_range_args
    def data_validation(self, first_row, first_col, last_row, last_col,
                        options):
        """
        Add a data validation to a worksheet.

        Args:
            first_row:    The first row of the cell range. (zero indexed).
            first_col:    The first column of the cell range.
            last_row:     The last row of the cell range. (zero indexed).
            last_col:     The last column of the cell range.
            options:      Data validation options.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.
            -2: Incorrect parameter or option.
        """
        # Check that row and col are valid without storing the values.
        if self._check_dimensions(first_row, first_col, True, True):
            return -1
        if self._check_dimensions(last_row, last_col, True, True):
            return -1

        # List of valid input parameters.
        valid_parameters = {
            'validate': True,
            'criteria': True,
            'value': True,
            'source': True,
            'minimum': True,
            'maximum': True,
            'ignore_blank': True,
            'dropdown': True,
            'show_input': True,
            'input_title': True,
            'input_message': True,
            'show_error': True,
            'error_title': True,
            'error_message': True,
            'error_type': True,
            'other_cells': True,
        }

        # Check for valid input parameters.
        for param_key in options.keys():
            if param_key not in valid_parameters:
                warn("Unknown parameter '%s' in data_validation()" % param_key)
                return -2

        # Map alternative parameter names 'source' or 'minimum' to 'value'.
        if 'source' in options:
            options['value'] = options['source']
        if 'minimum' in options:
            options['value'] = options['minimum']

        # 'validate' is a required parameter.
        if 'validate' not in options:
            warn("Parameter 'validate' is required in data_validation()")
            return -2

        # List of  valid validation types.
        valid_types = {
            'any': 'none',
            'any value': 'none',
            'whole number': 'whole',
            'whole': 'whole',
            'integer': 'whole',
            'decimal': 'decimal',
            'list': 'list',
            'date': 'date',
            'time': 'time',
            'text length': 'textLength',
            'length': 'textLength',
            'custom': 'custom',
        }

        # Check for valid validation types.
        if not options['validate'] in valid_types:
            warn("Unknown validation type '%s' for parameter "
                 "'validate' in data_validation()" % options['validate'])
            return -2
        else:
            options['validate'] = valid_types[options['validate']]

        # No action is required for validation type 'any' if there are no
        # input messages to display.
        if (options['validate'] == 'none'
            and options.get('input_title') is None
            and options.get('input_message') is None):
            return -2

        # The any, list and custom validations don't have a criteria so we use
        # a default of 'between'.
        if (options['validate'] == 'none'
            or options['validate'] == 'list'
            or options['validate'] == 'custom'):
            options['criteria'] = 'between'
            options['maximum'] = None

        # 'criteria' is a required parameter.
        if 'criteria' not in options:
            warn("Parameter 'criteria' is required in data_validation()")
            return -2

        # List of valid criteria types.
        criteria_types = {
            'between': 'between',
            'not between': 'notBetween',
            'equal to': 'equal',
            '=': 'equal',
            '==': 'equal',
            'not equal to': 'notEqual',
            '!=': 'notEqual',
            '<>': 'notEqual',
            'greater than': 'greaterThan',
            '>': 'greaterThan',
            'less than': 'lessThan',
            '<': 'lessThan',
            'greater than or equal to': 'greaterThanOrEqual',
            '>=': 'greaterThanOrEqual',
            'less than or equal to': 'lessThanOrEqual',
            '<=': 'lessThanOrEqual',
        }

        # Check for valid criteria types.
        if not options['criteria'] in criteria_types:
            warn("Unknown criteria type '%s' for parameter "
                 "'criteria' in data_validation()" % options['criteria'])
            return -2
        else:
            options['criteria'] = criteria_types[options['criteria']]

        # 'Between' and 'Not between' criteria require 2 values.
        if (options['criteria'] == 'between' or
                    options['criteria'] == 'notBetween'):
            if 'maximum' not in options:
                warn("Parameter 'maximum' is required in data_validation() "
                     "when using 'between' or 'not between' criteria")
                return -2
        else:
            options['maximum'] = None

        # List of valid error dialog types.
        error_types = {
            'stop': 0,
            'warning': 1,
            'information': 2,
        }

        # Check for valid error dialog types.
        if 'error_type' not in options:
            options['error_type'] = 0
        elif not options['error_type'] in error_types:
            warn("Unknown criteria type '%s' for parameter 'error_type' "
                 "in data_validation()" % options['error_type'])
            return -2
        else:
            options['error_type'] = error_types[options['error_type']]

        # Convert date/times value if required.
        if options['validate'] == 'date' or options['validate'] == 'time':

            if options['value']:
                if not supported_datetime(options['value']):
                    warn("Data validation 'value/minimum' must be a "
                         "datetime object.")
                    return -2
                else:
                    date_time = self._convert_date_time(options['value'])
                    if date_time == 0.0 and options['validate'] == 'date':
                        date_time = 1
                    # Format date number to the same precision as Excel.
                    options['value'] = "%.16g" % date_time

            if options['maximum']:
                if not supported_datetime(options['maximum']):
                    warn("Conditional format 'maximum' must be a "
                         "datetime object.")
                    return -2
                else:
                    date_time = self._convert_date_time(options['maximum'])
                    options['maximum'] = "%.16g" % date_time

        # Check that the input title doesn't exceed the maximum length.
        if options.get('input_title') and len(options['input_title']) > 32:
            warn("Length of input title '%s' exceeds Excel's limit of 32"
                 % force_unicode(options['input_title']))
            return -2

        # Check that the error title doesn't exceed the maximum length.
        if options.get('error_title') and len(options['error_title']) > 32:
            warn("Length of error title '%s' exceeds Excel's limit of 32"
                 % force_unicode(options['error_title']))
            return -2

        # Check that the input message doesn't exceed the maximum length.
        if (options.get('input_message')
            and len(options['input_message']) > 255):
            warn("Length of input message '%s' exceeds Excel's limit of 255"
                 % force_unicode(options['input_message']))
            return -2

        # Check that the error message doesn't exceed the maximum length.
        if (options.get('error_message')
            and len(options['error_message']) > 255):
            warn("Length of error message '%s' exceeds Excel's limit of 255"
                 % force_unicode(options['error_message']))
            return -2

        # Check that the input list doesn't exceed the maximum length.
        if options['validate'] == 'list' and type(options['value']) is list:
            formula = self._csv_join(*options['value'])
            if len(formula) > 255:
                warn("Length of list items '%s' exceeds Excel's limit of "
                     "255, use a formula range instead"
                     % force_unicode(formula))
                return -2

        # Set some defaults if they haven't been defined by the user.
        if 'ignore_blank' not in options:
            options['ignore_blank'] = 1
        if 'dropdown' not in options:
            options['dropdown'] = 1
        if 'show_input' not in options:
            options['show_input'] = 1
        if 'show_error' not in options:
            options['show_error'] = 1

        # These are the cells to which the validation is applied.
        options['cells'] = [[first_row, first_col, last_row, last_col]]

        # A (for now) undocumented parameter to pass additional cell ranges.
        if 'other_cells' in options:
            options['cells'].extend(options['other_cells'])

        # Store the validation information until we close the worksheet.
        self.validations.append(options)


class XlsTemplate(Workbook):
    chartsheet_class = Chartsheet
    worksheet_class = XlsWorkSheet

    def __init__(self, filename=None, options=None, properties=None):
        options = options or {}
        options.setdefault('default_date_format', 'D-MMM-YYYY')
        options.setdefault('default_datetime_format', 'DD MMM YYYY hh:mm')
        options.setdefault('default_time_format', 'hh:mm:ss')
        self.strings_to_numbers = True
        self._vba_added = False

        # self.default_time_format =
        # self.default_datetime_format = options.pop('default_datetime_format')
        self.timezone = options.pop('timezone', pytz.utc)

        super(XlsTemplate, self).__init__(filename, options)
        self.default_datetime_format = self.add_format({'num_format': options.pop('default_datetime_format')})
        self.default_time_format = self.add_format({'num_format': options.pop('default_time_format')})

        if properties:
            self.set_properties(properties)
            # self.set_properties({
            # 'title':    'This is an example spreadsheet',
            # 'subject':  'With document properties',
            # 'author':   'John McNamara',
            # 'manager':  'Dr. Heinz Doofenshmirtz',
            # 'company':  'of Wolves',
            # 'category': 'Example spreadsheets',
            # 'keywords': 'Sample, Example, Properties',
            # 'status': '',
            # 'comments': 'Created with Python and XlsxWriter'
        # })
        # self.set_custom_property("Creation Date", datetime.today(), "date")

        self.define_name('THIS', '=!A1')
        self.define_name('THIS_COL', '=!A')

    # def add_vba(self):
    #     if not self._vba_added:
    #         self.add_vba_project(os.path.join(os.path.dirname(__file__), 'vbaProject.bin'))
    #         self._vba_added = True
    def process_model(self, model, fields=None, exclude=None, queryset=None):
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

        for i, header in enumerate(sheet.headers):
            sheet.write(0, i, header.title, header.get_format())

        for i, col in enumerate(sheet.columns):
            col.process_workbook()

        # for row in range(1, 65000):
        #     for column in sheet.columns:
        #         column.format_cell(row, column.number)
        # for row in range(1, 65000):
        for column in sheet.columns:
            column.format_column()

        if queryset:
            for row, record in enumerate(queryset, 1):
                for colnum, column in enumerate(sheet.columns):
                    column.write_cell(row, colnum, record)

    # def add_worksheet(self, name=None, worksheet_class=None):
    #     """
    #     Add a new worksheet to the Excel workbook.
    #
    #     Args:
    #         name: The worksheet name. Defaults to 'Sheet1', etc.
    #
    #     Returns:
    #         Reference to a worksheet object.
    #
    #     """
    #     if worksheet_class is None:
    #         worksheet_class = self.worksheet_class
    #     return self._add_sheet(name, is_chartsheet=False, worksheet_class=worksheet_class)

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

        return worksheet

    def __del__(self):
        """Close file in destructor if it hasn't been closed explicitly."""
        try:
            if not self.fileclosed and self.filename:
                self.close()
        except:
            raise Exception("Exception caught in workbook destructor. "
                            "Explicit close() may be required for workbook.")
