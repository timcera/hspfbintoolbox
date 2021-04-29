#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
catalog
----------------------------------

Tests for `hspfbintoolbox` module.
"""

import shlex
import subprocess
from unittest import TestCase
from pandas.testing import assert_frame_equal
import sys

from tstoolbox import tsutils

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pandas as pd
from hspfbintoolbox import hspfbintoolbox


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, "utf-8")
    except:
        pass
    return out


class TestDescribe(TestCase):
    def setUp(self):
        self.extract = b"""Datetime,PERLND_905_AGWS_5
1950-01-01,0.844675
1951-01-01,1.0192
1952-01-01,0.267736
1953-01-01,1.19279
1954-01-01,1.33441
1955-01-01,0.00773311
1956-01-01,0.0935213
1957-01-01,1.09429
1958-01-01,0.223077
1959-01-01,1.53743
1960-01-01,0.860453
1961-01-01,0
1962-01-01,0.780285
1963-01-01,1.00642
1964-01-01,0.4788
1965-01-01,1.35207
1966-01-01,1.3705
1967-01-01,1.09639
1968-01-01,1.29344
1969-01-01,1.93707
1970-01-01,0.0277334
1971-01-01,1.26292
1972-01-01,0.967934
1973-01-01,1.25762
1974-01-01,1.16271
1975-01-01,1.32554
1976-01-01,1.25165
1977-01-01,1.77333
1978-01-01,1.58396
1979-01-01,1.16706
1980-01-01,0.109924
1981-01-01,0.237772
1982-01-01,1.31026
1983-01-01,1.86002
1984-01-01,0.881553
1985-01-01,0.494373
1986-01-01,1.23408
1987-01-01,0.773598
1988-01-01,0
1989-01-01,1.01879
1990-01-01,0.471807
1991-01-01,0.811257
1992-01-01,1.46362
1993-01-01,0.580862
1994-01-01,1.62932
1995-01-01,1.29516
1996-01-01,1.3109
1997-01-01,1.67992
1998-01-01,1.30317
1999-01-01,1.40244
2000-01-01,0.0191165
"""
        self.extract_api = StringIO(self.extract.decode())

    def test_extract_cli(self):
        args = "hspfbintoolbox extract tests/6b_np1.hbn yearly ,905,,AGWS"
        args = shlex.split(args)
        out = subprocess.Popen(
            args, stdout=subprocess.PIPE, stdin=subprocess.PIPE
        ).communicate()[0]
        self.assertEqual(out, self.extract)

    def test_extract_sub(self):
        out = hspfbintoolbox.extract("tests/6b_np1.hbn", "yearly", ",905,,AGWS")
        otherout = tsutils.asbestfreq(
            pd.read_csv(self.extract_api, header=0, index_col=0, parse_dates=True)
        )
        assert_frame_equal(out, otherout)
