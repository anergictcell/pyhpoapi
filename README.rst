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


Dev
===

Getting started for development
-------------------------------
Clone the repository

.. code:: bash

    git clone https://github.com/anergictcell/pyhpoapi.git
    cd pyhpoapi


Use Docker for development
--------------------------
One way to do this is to run a docker container during development

.. code:: bash
    docker run --rm -v $(pwd):/src -p 8000:8000 -it python:3.9-slim-buster bash

    cd src
    pip3 install -r requirements.txt
    pip3 install -r requirements-dev.txt

    python3 -m unittest discover tests

    uvicorn --host 0.0.0.0 --reload pyhpoapi.main:app


Or local development without Docker
-----------------------------------

Create a virtual environment and install requirements in the virtual environment


.. code:: bash

    virtualenv --python pyhon3 venv_pyhpoapi
    source venv_pyhpoapi/bin/activate

    pip3 install -r requirements.txt
    pip3 install -r requirements-dev.txt

    python3 -m unittest discover tests

    uvicorn --reload pyhpoapi.main:app


.. _PyHPO: https://esbme.com/pyhpo/docs/ 
