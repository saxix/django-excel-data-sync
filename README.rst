=====================
Django ExcelDataSync
=====================

.. image:: https://badge.fury.io/py/excel_data_sync.png
:target: https://badge.fury.io/py/excel_data_sync

.. image:: https://travis-ci.org/saxix/excel_data_sync.png?branch=master
:target: https://travis-ci.org/saxix/excel_data_sync


It allows to create XLS file to import data into Django Model.
The xls implement most of the validation rules of the django model fields, this
prevent errors due the lack of constraints


Supported Fields
----------------
BigIntegerField
BooleanField
CharField
DateField
DateTimeField
DecimalField
EmailField
FloatField
ForeignKey
GenericIPAddressField
IntegerField
NullBooleanField*
PositiveIntegerField
PositiveSmallIntegerField
SmallIntegerField
TextField
TimeField
URLField
UUIDField

Supported Validations
---------------------
unique
max value
min value
max length
min length


Documentation
-------------

The full documentation is at https://excel_data_sync.readthedocs.io.

Quickstart
----------

Install ExcelDataSync::

    pip install django-excel-data-sync

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'excel_data_sync.apps.XlsDataSyncConfig',
        ...
    )

Add ExcelDataSync's URL patterns:

.. code-block:: python

    from excel_data_sync import urls as excel_data_sync_urls


    urlpatterns = [
        ...
        url(r'^', include(excel_data_sync_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
