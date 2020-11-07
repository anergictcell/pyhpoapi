*********
PyHPO-API
*********

A HTTP REST-API wrapper for `PyHPO`_

Main features
=============
This package allows an easy setup of a REST API to interact with HPO Terms using the `PyHPO`_ package.


Installation / Setup
====================

The easiest way to install PyHPO-API is via pip

.. code:: bash

    pip install pyhpoapi


Usage
=====

Getting started
---------------
The easiest way to get started is to run the API via

.. code:: bash

    uvicorn pyhpoapi.main:app


Parallel processing
-------------------
If you want better performance for parallel request handling,
you can run PyHPO-API with multiple workers

.. code:: bash

    uvicorn pyhpoapi.main:app --workers 15 


.. note::

    Don't use more workers than available CPUs as it will backfire
    and slow down processing due to constant context-switches

CORS
----
If you need to allow cross-origin requests, you can simply create
a ``config.ini`` file in your working directory and specify CORS settings::

    [default]
    cors-origins = *
    cors-methods = GET,POST
    cors-headers = *



.. _PyHPO: https://esbme.com/pyhpo/docs/ 
