====================
Django ExcelDataSync
====================

.. image:: https://badge.fury.io/py/django_excel_data_sync.png
    :target: https://badge.fury.io/py/django_excel_data_sync

.. image:: https://travis-ci.org/saxix/django-excel-data-sync.png?branch=develop
    :target: https://travis-ci.org/saxix/django-excel-data-sync


It allows to create XLS file to import data into Django Model.
The xls implements most of the validation rules of the django model fields, this
prevent errors due the lack of constraints


Supported Fields
----------------

    - BigIntegerField
    - BooleanField
    - AutoField
    - CharField
    - DateField
    - DateTimeField
    - DecimalField
    - EmailField
    - FloatField
    - ForeignKey
    - GenericIPAddressField
    - IntegerField
    - NullBooleanField*
    - PositiveIntegerField
    - PositiveSmallIntegerField
    - SmallIntegerField
    - TextField
    - TimeField
    - URLField
    - UUIDField

Supported Validations
---------------------

Fields attributes
~~~~~~~~~~~~~~~~~

    - choices
    - unique


Field Validators
~~~~~~~~~~~~~~~~


    - max value (`MaxValueValidator`)
    - min value (`MinValueValidator`)
    - max length `MaxLengthValidator`)
    - min length (`MinLengthValidator`)


Documentation
-------------

The full documentation is at http://django-excel-data-sync.readthedocs.io/en/latest/

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


Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

