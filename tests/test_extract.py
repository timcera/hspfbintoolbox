# -*- coding: utf-8 -*-

"""
catalog
----------------------------------

Tests for `hspfbintoolbox` module.
"""

import shlex
import subprocess
import sys
from unittest import TestCase

from pandas.testing import assert_frame_equal
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
        self.extract = b"""Datetime,PERLND_905_AGWS
1950,0.844675
1951,1.0192
1952,0.267736
1953,1.19279
1954,1.33441
1955,0.00773311
1956,0.0935213
1957,1.09429
1958,0.223077
1959,1.53743
1960,0.860453
1961,0
1962,0.780285
1963,1.00642
1964,0.4788
1965,1.35207
1966,1.3705
1967,1.09639
1968,1.29344
1969,1.93707
1970,0.0277334
1971,1.26292
1972,0.967934
1973,1.25762
1974,1.16271
1975,1.32554
1976,1.25165
1977,1.77333
1978,1.58396
1979,1.16706
1980,0.109924
1981,0.237772
1982,1.31026
1983,1.86002
1984,0.881553
1985,0.494373
1986,1.23408
1987,0.773598
1988,0
1989,1.01879
1990,0.471807
1991,0.811257
1992,1.46362
1993,0.580862
1994,1.62932
1995,1.29516
1996,1.3109
1997,1.67992
1998,1.30317
1999,1.40244
2000,0.0191165
"""
        self.extract_api = StringIO(self.extract.decode())

    def test_extract_one_label_cli(self):
        args = "hspfbintoolbox extract tests/data_yearly.hbn yearly ,905,,AGWS"
        args = shlex.split(args)
        out = subprocess.Popen(
            args, stdout=subprocess.PIPE, stdin=subprocess.PIPE
        ).communicate()[0]
        self.assertEqual(out, self.extract)

    def test_extract_one_label_labellist_api(self):
        out = hspfbintoolbox.extract(
            "tests/data_yearly.hbn", "yearly", ["", 905, "", "AGWS"]
        )
        otherout = tsutils.asbestfreq(
            pd.read_csv(self.extract_api, header=0, index_col=0, parse_dates=True)
        )
        otherout.index = otherout.index.to_period()
        assert_frame_equal(out, otherout)

    def test_extract_one_label_labelstr_api(self):
        out = hspfbintoolbox.extract("tests/data_yearly.hbn", "yearly", ",905,,AGWS")
        otherout = tsutils.asbestfreq(
            pd.read_csv(self.extract_api, header=0, index_col=0, parse_dates=True)
        )
        otherout.index = otherout.index.to_period()
        assert_frame_equal(out, otherout)
