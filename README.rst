.. image:: https://github.com/timcera/hspfbintoolbox/actions/workflows/python-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/hspfbintoolbox/actions/workflows/python-package.yml
    :height: 20

.. image:: https://img.shields.io/coveralls/github/timcera/hspfbintoolbox
    :alt: Test Coverage
    :target: https://coveralls.io/r/timcera/hspfbintoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/hspfbintoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/hspfbintoolbox/
    :height: 20

.. image:: http://img.shields.io/pypi/l/hspfbintoolbox.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/hspfbintoolbox/
    :height: 20

.. image:: http://img.shields.io/pypi/dd/hspfbintoolbox.svg
    :alt: hspfbintoolbox downloads
    :target: https://pypi.python.org/pypi/hspfbintoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/pyversions/hspfbintoolbox
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/hspfbintoolbox/
    :height: 20

Documentation for hspfbintoolbox
================================
The ``hspfbintoolbox`` is a Python script and library of functions to read
Hydrological Simulation Program Fortran (HSPF) binary files and print to
screen.  The time series can then be redirected to file, or piped to other
command line programs like ``tstoolbox``.

Requirements
------------

* python 3.7 or later

* tstoolbox - utilities to process time-series

Installation
------------
pip
~~~
.. code-block:: bash

    pip install hspfbintoolbox

conda
~~~~~
.. code-block:: bash

    conda install -c conda-forge hspfbintoolbox


Usage - Command Line
--------------------
Just run 'hspfbintoolbox --help' to get a list of subcommands:

 catalog
          Prints out a catalog of data sets in the binary file.

 extract
          Prints out data to the screen from a HSPF binary output file.

For the subcommands that output data it is printed to the screen and you can
then redirect to a file.

Usage - API
-----------
You can use all of the command line subcommands as functions.  The function
signature is identical to the command line subcommands.  The return is always
a PANDAS DataFrame.  Input can be a CSV or TAB separated file, or a PANDAS
DataFrame and is supplied to the function via the 'input_ts' keyword.

Simply import hspfbintoolbox::

    import hspfbintoolbox

    # Then you could call the functions
    ntsd = hspfbintoolbox.extract('tests/test.hbn', 'yearly', ',905,,AGWS')

    # Once you have a PANDAS DataFrame you can use that as input.
    ntsd = tstoolbox.aggregate(statistic='mean', agg_interval='daily', input_ts=ntsd)
