Usage
=====

.. _installation:

Installation
------------

To use the app, first install the dependencies using pip:

.. code-block:: console

   (.venv) $ pip install -r requirement.txt

Starting the Application
------------------------

To start the app, use the fastapi cli from the project root

.. code-block:: console

    (.venv) $ fastapi run ./src/app.py

Testing the Application
------------------------

To test the app, use pytest with the test.py script

.. code-block:: console

    (.venv) $ pytest ./src/test.py


Adding Own Data to the Application
----------------------------------

.. role:: python(code)
   :language: python

To add your own data duplicate or modify insert.sql

If file name changes find :python:`INSERT_SCRIPT = ""` in :code:`app.py`

and modify the value
