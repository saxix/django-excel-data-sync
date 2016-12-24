====================
Django ExcelDataSync
====================

.. image:: https://badge.fury.io/py/django-excel-data-sync.svg
    :target: https://badge.fury.io/py/django-excel-data-sync

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


Project links
-------------

+--------------------+----------------+--------------+----------------------------+
| Stable             | |master-build| | |master-cov| |                            |
+--------------------+----------------+--------------+----------------------------+
| Development        | |dev-build|    | |dev-cov|    |                            |
+--------------------+----------------+--------------+----------------------------+
| Project home page: |https://github.com/saxix/django-excel-data-sync             |
+--------------------+---------------+--------------------------------------------+
| Issue tracker:     |https://github.com/saxix/django-excel-data-sync/issues?sort |
+--------------------+---------------+--------------------------------------------+
| Download:          |http://pypi.python.org/pypi/django-excel-data-sync/         |
+--------------------+---------------+--------------------------------------------+
| Documentation:     |https://django-excel-data-sync.readthedocs.org/en/latest/   |
+--------------------+---------------+--------------+-----------------------------+



.. |master-build| image:: https://secure.travis-ci.org/saxix/django-excel-data-sync.png?branch=master
                    :target: http://travis-ci.org/saxix/django-excel-data-sync/

.. |master-cov| image:: https://codecov.io/github/saxix/django-excel-data-sync/coverage.svg?branch=master
    :target: https://codecov.io/github/saxix/django-excel-data-sync?branch=master


.. |dev-build| image:: https://secure.travis-ci.org/saxix/django-excel-data-sync.png?branch=develop
                  :target: http://travis-ci.org/saxix/django-excel-data-sync/

.. |dev-cov| image:: https://codecov.io/github/saxix/django-excel-data-sync/coverage.svg?branch=develop
    :target: https://codecov.io/github/saxix/django-excel-data-sync?branch=develop
