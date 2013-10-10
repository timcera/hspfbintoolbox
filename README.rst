HSPFBINTOOLBOX
==============
The hspfbintoolbox is a Python script to read Hydrological Simulation Program
Fortran (HSPF) binary files and print to screen.  The time series can then be
redirected to file, or piped to other command line programs like `tstoolbox`.

Requirements
============

* pandas - on Windows this is part of the Python(x,y) distribution
  (http://code.google.com/p/pythonxy/)

* baker - command line parser

* tstoolbox - utilities to process time-series

* construct - a binary parser

Installation
============
Should be as easy as running ``easy_install hspfbintoolbox`` or ``pip install
hspfbintoolbox``` at any command line.  Not sure on Windows whether this will
bring in pandas but as mentioned above, if you start with Python(x,y) then you
won't have a problem.

Running
=======
Just run 'hspfbintoolbox.py' to get a list of subcommands::

    Usage: /sjr/beodata/local/python_linux/bin/hspfbintoolbox COMMAND <options>
    
    Available commands:
     catalog
     dump
     time_series  Prints out data to the screen from a HSPF binary output file.
    
    Use '/sjr/beodata/local/python_linux/bin/hspfbintoolbox <command> --help' for individual command help.

Author
======
Tim Cera, P.E.

tim at cerazone dot net

Please send me a note if you find this useful, found a bug, submit a patch,
...etc.

