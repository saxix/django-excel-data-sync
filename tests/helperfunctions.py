###############################################################################
#
# Helper functions for testing XlsxWriter.
#
# Copyright (c), 2013-2016, John McNamara, jmcnamara@cpan.org
#

import errno
import os.path
import re
import six
import sys
from contextlib import contextmanager
from zipfile import BadZipfile, LargeZipFile, ZipFile

from excel_data_sync.columns import mapping, register_column, unregister_column

here = os.path.dirname(__file__)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def _xml_to_list(xml_str):
    # Convert test generated XML strings into lists for comparison testing.

    # Split the XML string at tag boundaries.
    parser = re.compile(r'>\s*<')
    elements = parser.split(xml_str.strip())

    elements = [s.replace("\r", "") for s in elements]

    # Add back the removed brackets.
    for index, element in enumerate(elements):
        if not element[0] == '<':
            elements[index] = '<' + elements[index]
        if not element[-1] == '>':
            elements[index] = elements[index] + '>'

    return elements


def _vml_to_list(vml_str):
    # Convert an Excel generated VML string into a list for comparison testing.
    #
    # The VML data in the testcases is taken from Excel 2007 files. The data
    # has to be massaged significantly to make it suitable for comparison.
    #
    # The VML produced by XlsxWriter can be parsed as ordinary XML.
    vml_str = vml_str.replace("\r", "")

    vml = vml_str.split("\n")
    vml_str = ''

    for line in vml:
        # Skip blank lines.
        if not line:
            continue

        # Strip leading and trailing whitespace.
        line = line.strip()

        # Convert VMLs attribute quotes.
        line = line.replace("'", '"')

        # Add space between attributes.
        if re.search('"$', line):
            line += " "

        # Add newline after element end.
        if re.search('>$', line):
            line += "\n"

        # Split multiple elements.
        line = line.replace('><', ">\n<")

        # Put all of Anchor on one line.
        if line == "<x:Anchor>\n":
            line = line.strip()

        vml_str += line

    # Remove the final newline.
    vml_str = vml_str.rstrip()

    return vml_str.split("\n")


def _sort_rel_file_data(xml_elements):
    # Re-order the relationship elements in an array of XLSX XML rel
    # (relationship) data. This is necessary for comparison since
    # Excel can produce the elements in a semi-random order.

    # We don't want to sort the first or last elements.
    first = xml_elements.pop(0)
    last = xml_elements.pop()

    # Sort the relationship elements.
    xml_elements.sort()

    # Add back the first and last elements.
    xml_elements.insert(0, first)
    xml_elements.append(last)

    return xml_elements


def get_target_xls(name):
    target = os.path.join(here, 'data', name)
    if not os.path.exists(os.path.dirname(target)):
        mkdir_p(os.path.dirname(target))
    return target
    # return os.path.join(here, 'data', str(sys.version_info[0]), name)


def get_io(n):
    if os.path.exists(n):
        return six.BytesIO()
    return n


@contextmanager
def register(key, col):
    old = None
    if key in mapping:
        old = mapping[key]
    register_column(key, col)
    yield
    unregister_column(key)
    if old:
        register_column(key, old)


def _compare_xlsx_files(got_file, exp_file,  # noqa
                        ignore_files=[],
                        ignore_elements={},
                        clean_value={},
                        limit_to_files=None,
                        ignore_re=None):  # noqa
    # Compare two XLSX files by extracting the XML files from each
    # zip archive and comparing them.
    #
    # This is used to compare an "expected" file produced by Excel
    # with a "got" file produced by XlsxWriter.
    #
    # In order to compare the XLSX files we convert the data in each
    # XML file into an list of XML elements.
    try:
        # Open the XlsxWriter as a zip file for testing.
        got_zip = ZipFile(got_file, 'r')
    except IOError:
        # For Python 2.5+ compatibility.
        e = sys.exc_info()[1]
        error = "XlsxWriter file error: " + str(e)
        return error, ''
    except (BadZipfile, LargeZipFile):
        e = sys.exc_info()[1]
        error = "XlsxWriter zipfile error, '" + exp_file + "': " + str(e)
        return error, ''

    try:
        # Open the Excel as a zip file for testing.
        exp_zip = ZipFile(exp_file, 'r')
    except IOError:
        e = sys.exc_info()[1]
        error = "Excel file error: " + str(e)
        return error, ''
    except (BadZipfile, LargeZipFile):
        e = sys.exc_info()[1]
        error = "Excel zipfile error, '" + exp_file + "': " + str(e)
        return error, ''

    # Get the filenames from the zip files.
    got_files = sorted(got_zip.namelist())
    exp_files = sorted(exp_zip.namelist())
    if limit_to_files:
        # Ignore some test specific filenames.
        got_files = [name for name in got_files if name in limit_to_files]
        exp_files = [name for name in exp_files if name in limit_to_files]
    else:
        # Ignore some test specific filenames.
        got_files = [name for name in got_files if name not in ignore_files]
        exp_files = [name for name in exp_files if name not in ignore_files]

    # Check that each XLSX container has the same files.
    if got_files != exp_files:
        return got_files, exp_files

    # Compare each file in the XLSX containers.
    for filename in exp_files:
        got_xml_str = got_zip.read(filename)
        exp_xml_str = exp_zip.read(filename)

        # Compare binary files with string comparison based on extension.
        extension = os.path.splitext(filename)[1]
        if extension in ('.png', '.jpeg', '.bmp', '.bin'):
            if got_xml_str != exp_xml_str:
                return 'got: %s' % filename, 'exp: %s' % filename
            continue

        if sys.version_info >= (3, 0, 0):
            got_xml_str = got_xml_str.decode('utf-8')
            exp_xml_str = exp_xml_str.decode('utf-8')

        # Remove dates and user specific data from the core.xml data.
        if filename == 'docProps/app.xml':
            exp_xml_str = re.sub(r'<Application>[^<]*',
                                 '<Application>', exp_xml_str, re.DOTALL)
            got_xml_str = re.sub(r'<Application>[^<]*',
                                 '<Application>', got_xml_str, re.DOTALL)

        # Remove dates and user specific data from the core.xml data.
        if filename == 'docProps/custom.xml':
            exp_xml_str = re.sub(r'name="Creation Date"><vt:filetime>[^<]*',
                                 'name="Creation Date"><vt:filetime>', exp_xml_str)
            got_xml_str = re.sub(r'name="Creation Date"><vt:filetime>[^<]*',
                                 'name="Creation Date"><vt:filetime>', got_xml_str)

        if filename == 'docProps/core.xml':
            exp_xml_str = re.sub(r'<cp:lastModifiedBy>[^<]*', '', exp_xml_str)
            got_xml_str = re.sub(r'<cp:lastModifiedBy>[^<]*', '', got_xml_str)

            exp_xml_str = re.sub(r' ?John', '', exp_xml_str)
            exp_xml_str = re.sub(r'\d\d\d\d-\d\d-\d\dT\d\d\:\d\d:\d\dZ',
                                 '', exp_xml_str)
            got_xml_str = re.sub(r'\d\d\d\d-\d\d-\d\dT\d\d\:\d\d:\d\dZ',
                                 '', got_xml_str)

        # Remove workbookView dimensions which are almost always different
        # and calcPr which can have different Excel version ids.
        if filename == 'xl/workbook.xml':
            exp_xml_str = re.sub(r'<workbookView[^>]*>',
                                 '<workbookView/>', exp_xml_str)
            got_xml_str = re.sub(r'<workbookView[^>]*>',
                                 '<workbookView/>', got_xml_str)
            exp_xml_str = re.sub(r'<calcPr[^>]*>',
                                 '<calcPr/>', exp_xml_str)
            got_xml_str = re.sub(r'<calcPr[^>]*>',
                                 '<calcPr/>', got_xml_str)

        # Remove printer specific settings from Worksheet pageSetup elements.
        if re.match(r'xl/worksheets/sheet\d.xml', filename):
            exp_xml_str = re.sub(r'horizontalDpi="200" ', '', exp_xml_str)
            exp_xml_str = re.sub(r'verticalDpi="200" ', '', exp_xml_str)
            exp_xml_str = re.sub(r'(<pageSetup[^>]*) r:id="rId1"',
                                 r'\1', exp_xml_str)

        # Remove Chart pageMargin dimensions which are almost always different.
        if re.match(r'xl/charts/chart\d.xml', filename):
            exp_xml_str = re.sub(r'<c:pageMargins[^>]*>',
                                 '<c:pageMargins/>', exp_xml_str)
            got_xml_str = re.sub(r'<c:pageMargins[^>]*>',
                                 '<c:pageMargins/>', got_xml_str)

        if ignore_re and filename in ignore_re:
            patterns = ignore_re[filename]
            for pattern in patterns:
                match, sub = pattern
                exp_xml_str = re.sub(match, sub, exp_xml_str, re.DOTALL)
                got_xml_str = re.sub(match, sub, got_xml_str, re.DOTALL)

        # Convert the XML string to lists for comparison.
        if re.search('.vml$', filename):
            got_xml = _xml_to_list(got_xml_str)
            exp_xml = _vml_to_list(exp_xml_str)
        else:
            got_xml = _xml_to_list(got_xml_str)
            exp_xml = _xml_to_list(exp_xml_str)

        # Ignore test specific XML elements for defined filenames.
        if filename in clean_value:
            patterns = clean_value[filename]
            for pattern in patterns:
                for i, tag in enumerate(got_xml):
                    if re.match(pattern, tag):
                        got_xml[i + 1] = ''
                for i, tag in enumerate(exp_xml):
                    if re.match(pattern, tag):
                        exp_xml[i + 1] = ''

        if filename in ignore_elements:
            patterns = ignore_elements[filename]

            for pattern in patterns:
                exp_xml = [tag for tag in exp_xml if not re.match(pattern, tag)]
                got_xml = [tag for tag in got_xml if not re.match(pattern, tag)]

        # Reorder the XML elements in the XLSX relationship files.
        if filename == '[Content_Types].xml' or re.search('.rels$', filename):
            got_xml = _sort_rel_file_data(got_xml)
            exp_xml = _sort_rel_file_data(exp_xml)

        # Compared the XML elements in each file.
        if got_xml != exp_xml:
            got_xml.insert(0, filename)
            exp_xml.insert(0, filename)
            return got_xml, exp_xml

    # If we got here the files are the same.
    return 'Ok', 'Ok'


def _check_format(xls_file):
    try:
        # Open the Excel as a zip file for testing.
        exp_zip = ZipFile(xls_file, 'r')
    except IOError:
        e = sys.exc_info()[1]
        error = "Excel file error: " + str(e)
        return error, ''
    except (BadZipfile, LargeZipFile):
        e = sys.exc_info()[1]
        error = "Excel zipfile error, '" + xls_file + "': " + str(e)
        return error, ''
    exp_zip.extractall(os.path.join(os.path.dirname(xls_file), 'aaa'))
