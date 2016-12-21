=====
Usage
=====

To use Django Excel Data Sync in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'excel_data_sync.apps.XlsUploaderConfig',
        ...
    )

Add Excel Data Sync's URL patterns:

.. code-block:: python

    from excel_data_sync import urls as excel_data_sync_urls


    urlpatterns = [
        ...
        url(r'^', include(excel_data_sync_urls)),
        ...
    ]
