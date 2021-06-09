.. image:: https://travis-ci.org/timcera/hspfbintoolbox.svg?branch=master
    :target: https://travis-ci.org/timcera/hspfbintoolbox
    :height: 20

.. image:: https://coveralls.io/repos/timcera/hspfbintoolbox/badge.png?branch=master
    :target: https://coveralls.io/r/timcera/hspfbintoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/hspfbintoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/hspfbintoolbox

.. image:: http://img.shields.io/badge/license-BSD-lightgrey.svg
    :alt: hspfbintoolbox license
    :target: https://pypi.python.org/pypi/hspfbintoolbox/

Documentation for hspfbintoolbox
================================
The ``hspfbintoolbox`` is a Python script and library of functions to read
Hydrological Simulation Program Fortran (HSPF) binary files and print to
screen.  The time series can then be redirected to file, or piped to other
command line programs like ``tstoolbox``.

Requirements
------------

* pandas - on Windows this is part of the Python(x,y), Enthought, or
  Anaconda distributions

* mando - command line parser

* tstoolbox - utilities to process time-series

Installation
------------
Should be as easy as running ``pip install hspfbintoolbox`` or ``easy_install
hspfbintoolbox`` at any command line.  Not sure on Windows whether this will
bring in pandas but as mentioned above, if you start with Python(x,y) then
you won't have a problem.

Usage - Command Line
--------------------
Just run 'hspfbintoolbox' to get a list of subcommands:

 catalog
          Prints out a catalog of data sets in the binary file.

 dump
          Prints out ALL data from a HSPF binary output file.

 extract
          Prints out data to the screen from a HSPF binary output file.

 time_series
          DEPRECATED: Use 'extract' instead.

The default for all of the subcommands is to accept data from stdin
(typically a pipe).  If a subcommand accepts an input file for an argument,
you can use "--infile=filename", or to explicitly specify from stdin use
"--infile='-'" .

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
    ntsd = hspfbintoolbox.dump('tests/test.hbn')

    # Once you have a PANDAS DataFrame you can use that as input.
    ntsd = tstoolbox.aggregate(statistic='mean', agg_interval='daily', input_ts=ntsd)
