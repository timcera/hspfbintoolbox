#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
catalog
----------------------------------

Tests for `hspfbintoolbox` module.
"""

import csv
import shlex
import subprocess
from unittest import TestCase
from pandas.testing import assert_frame_equal
import sys

try:
    from cStringIO import StringIO
except:
    from io import StringIO

import pandas as pd
from hspfbintoolbox import hspfbintoolbox

interval2codemap = {"yearly": 5, "monthly": 4, "daily": 3, "bivl": 2}


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, "utf-8")
    except:
        pass
    return out


def read_unicode_csv(
    filename,
    delimiter=",",
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
    lineterminator="\n",
    encoding="utf-8",
):
    # Python 3 version
    if sys.version_info[0] >= 3:
        # Open the file in text mode with given encoding
        # Set newline arg to ''
        # (see https://docs.python.org/3/library/csv.html)
        # Next, get the csv reader, with unicode delimiter and quotechar
        csv_reader = csv.reader(
            filename,
            delimiter=delimiter,
            quotechar=quotechar,
            quoting=quoting,
            lineterminator=lineterminator,
        )
        # Now, iterate over the (already decoded) csv_reader generator
        for row in csv_reader:
            yield row
    # Python 2 version
    else:
        # Next, get the csv reader, passing delimiter and quotechar as
        # bytestrings rather than unicode
        csv_reader = csv.reader(
            filename,
            delimiter=delimiter.encode(encoding),
            quotechar=quotechar.encode(encoding),
            quoting=quoting,
            lineterminator=lineterminator,
        )
        # Iterate over the file and decode each string into unicode
        for row in csv_reader:
            yield [cell.decode(encoding) for cell in row]


class TestDescribe(TestCase):
    def setUp(self):
        self.catalog = b"""\
LUE   ,  LC,GROUP  ,VAR  ,  TC,START  ,END  ,TC
IMPLND,  11,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  11,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  11,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  11,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  11,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  11,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  12,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  12,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  12,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  12,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  12,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  12,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  13,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  13,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  13,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  13,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  13,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  13,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  14,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  14,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  14,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  14,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  14,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  14,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  21,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  21,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  21,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  21,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  21,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  21,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  22,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  22,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  22,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  22,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  22,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  22,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  23,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  23,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  23,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  23,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  23,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  23,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  24,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  24,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  24,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  24,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  24,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  24,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  31,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  31,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  31,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  31,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  31,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  31,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  32,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  32,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  32,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  32,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  32,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  32,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND,  33,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND,  33,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND,  33,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND,  33,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND,  33,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND,  33,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 111,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 111,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 111,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 111,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 111,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 111,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 112,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 112,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 112,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 112,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 112,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 112,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 113,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 113,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 113,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 113,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 113,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 113,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 114,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 114,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 114,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 114,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 114,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 114,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 211,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 211,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 211,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 211,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 211,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 211,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 212,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 212,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 212,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 212,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 212,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 212,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 213,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 213,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 213,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 213,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 213,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 213,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 214,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 214,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 214,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 214,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 214,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 214,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 301,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 301,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 301,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 301,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 301,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 301,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 302,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 302,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 302,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 302,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 302,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 302,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 303,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 303,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 303,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 303,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 303,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 303,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 304,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 304,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 304,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 304,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 304,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 304,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 311,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 311,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 311,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 311,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 311,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 311,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 312,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 312,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 312,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 312,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 312,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 312,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 313,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 313,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 313,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 313,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 313,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 313,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 314,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 314,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 314,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 314,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 314,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 314,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 411,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 411,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 411,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 411,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 411,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 411,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 412,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 412,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 412,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 412,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 412,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 412,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 413,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 413,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 413,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 413,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 413,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 413,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 414,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 414,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 414,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 414,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 414,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 414,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 511,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 511,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 511,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 511,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 511,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 511,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 512,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 512,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 512,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 512,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 512,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 512,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 513,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 513,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 513,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 513,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 513,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 513,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 514,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 514,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 514,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 514,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 514,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 514,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 611,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 611,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 611,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 611,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 611,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 611,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 612,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 612,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 612,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 612,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 612,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 612,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 613,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 613,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 613,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 613,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 613,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 613,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 614,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 614,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 614,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 614,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 614,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 614,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 711,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 711,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 711,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 711,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 711,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 711,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 712,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 712,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 712,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 712,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 712,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 712,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 713,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 713,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 713,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 713,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 713,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 713,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 714,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 714,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 714,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 714,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 714,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 714,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 811,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 811,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 811,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 811,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 811,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 811,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 812,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 812,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 812,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 812,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 812,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 812,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 813,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 813,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 813,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 813,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 813,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 813,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 814,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 814,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 814,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 814,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 814,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 814,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 822,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 822,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 822,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 822,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 822,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 822,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 823,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 823,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 823,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 823,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 823,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 823,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 824,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 824,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 824,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 824,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 824,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 824,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 901,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 901,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 901,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 901,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 901,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 901,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 902,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 902,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 902,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 902,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 902,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 902,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 903,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 903,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 903,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 903,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 903,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 903,IWATER ,SURS ,   5,1951   ,2001 ,yearly
IMPLND, 904,IWATER ,IMPEV,   5,1951   ,2001 ,yearly
IMPLND, 904,IWATER ,PET  ,   5,1951   ,2001 ,yearly
IMPLND, 904,IWATER ,RETS ,   5,1951   ,2001 ,yearly
IMPLND, 904,IWATER ,SUPY ,   5,1951   ,2001 ,yearly
IMPLND, 904,IWATER ,SURO ,   5,1951   ,2001 ,yearly
IMPLND, 904,IWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  11,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  12,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  13,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  14,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  15,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  21,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  22,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  23,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  24,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  25,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  31,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  32,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  33,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND,  35,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 111,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 112,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 113,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 114,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 115,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 211,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 212,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 213,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 214,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 215,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 301,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 302,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 303,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 304,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 305,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 311,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 312,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 313,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 314,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 315,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 411,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 412,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 413,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 414,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 415,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 511,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 512,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 513,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 514,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 515,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 611,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 612,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 613,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 614,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 615,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 711,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 712,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 713,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 714,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 715,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 811,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 812,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 813,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 814,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 815,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 822,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 823,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 824,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 825,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 901,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 902,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 903,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 904,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,AGWET,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,AGWI ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,AGWO ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,AGWS ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,BASET,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,CEPE ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,CEPS ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,GWVS ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,IFWI ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,IFWO ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,IFWS ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,IGWI ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,INFIL,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,LZET ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,LZI  ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,LZS  ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,PERC ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,PERO ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,PERS ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,PET  ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,SUPY ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,SURO ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,SURS ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,TAET ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,UZET ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,UZI  ,   5,1951   ,2001 ,yearly
PERLND, 905,PWATER ,UZS  ,   5,1951   ,2001 ,yearly
"""
        ndict = []
        rd = read_unicode_csv(StringIO(self.catalog.decode()))
        next(rd)
        for row in rd:
            if len(row) == 0:
                continue
            nrow = [i.strip() for i in row]
            ndict.append(
                (nrow[0], int(nrow[1]), nrow[2], nrow[3], interval2codemap[nrow[7]])
            )
        self.ncatalog = sorted(ndict)

    def test_catalog_api(self):
        out = hspfbintoolbox.catalog("tests/6b_np1.hbn")
        out = [i[:5] for i in out]
        self.assertEqual(out, self.ncatalog)

    def test_catalog_cli(self):
        args = "hspfbintoolbox catalog --tablefmt csv tests/6b_np1.hbn"
        args = shlex.split(args)
        out = subprocess.Popen(
            args, stdout=subprocess.PIPE, stdin=subprocess.PIPE
        ).communicate()[0]
        self.assertEqual(out, self.catalog)
