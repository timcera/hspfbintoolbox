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
from toolbox_utils import tsutils

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
    except Exception:
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

        self.extract_range = b"""Datetime,PERLND_901_AGWS,PERLND_902_AGWS,PERLND_903_AGWS,PERLND_905_AGWS
1950,2.71719e-06,0.0387649,0.0101779,0.844675
1951,1.11058e-08,0.0948097,0.0136074,1.0192
1952,1.10301e-06,0.0497635,0.00574832,0.267736
1953,0.0679923,0.071584,0.0957061,1.19279
1954,0.00106189,0.168513,0.0392933,1.33441
1955,0.0918087,0.149497,0.0610277,0.00773311
1956,9.65553e-06,0.0428243,0.00881373,0.0935213
1957,0.055891,0.56924,0.278232,1.09429
1958,0.120286,0.425905,0.25168,0.223077
1959,0.0388658,0.140838,0.118875,1.53743
1960,0.00401418,0.140998,0.0430524,0.860453
1961,3.94134e-05,0.141588,0.0256914,0
1962,0.00240514,0.0656636,0.0247286,0.780285
1963,0.431542,0.970387,0.503066,1.00642
1964,0.0479436,0.295537,0.129303,0.4788
1965,0.00437566,0.250931,0.0816154,1.35207
1966,0.000117049,0.0406975,0.0209651,1.3705
1967,0.0785445,0.375869,0.153903,1.09639
1968,0.0889516,0.12408,0.0593081,1.29344
1969,0.000776831,0.116923,0.0423577,1.93707
1970,0.117868,0.145729,0.0866315,0.0277334
1971,0.0382708,0.259635,0.12201,1.26292
1972,0.0185205,0.386784,0.136546,0.967934
1973,0.0158888,0.302976,0.112111,1.25762
1974,0.00785923,0.250649,0.112572,1.16271
1975,0.0104612,0.128357,0.0634007,1.32554
1976,0.186341,0.39664,0.162471,1.25165
1977,0.00305537,0.383265,0.129511,1.77333
1978,0.162075,0.941923,0.446787,1.58396
1979,0.000374656,0.157546,0.0447748,1.16706
1980,0.0174261,0.426128,0.170246,0.109924
1981,0.162457,0.235762,0.106183,0.237772
1982,0.00185585,0.132443,0.0643838,1.31026
1983,0.291482,0.765218,0.332954,1.86002
1984,0.0222107,0.202498,0.0968264,0.881553
1985,0.00306275,0.103119,0.0462879,0.494373
1986,0.414932,1.00972,0.428948,1.23408
1987,7.0159e-10,0.0755958,0.00837575,0.773598
1988,0.000930488,0.185656,0.0509336,0
1989,0.00776226,0.502512,0.20519,1.01879
1990,2.23688e-10,0.0337445,0.00298782,0.471807
1991,2.75944e-13,0.0176705,0.000876624,0.811257
1992,0.0788673,0.15709,0.09928,1.46362
1993,0.0369706,0.429546,0.189063,0.580862
1994,0.00182149,0.409419,0.167483,1.62932
1995,0.00496527,0.0119555,0.0393507,1.29516
1996,0.0601164,0.182465,0.072205,1.3109
1997,0.0116886,0.486823,0.162227,1.67992
1998,1.3452e-05,0.0325279,0.0143696,1.30317
1999,0.00138731,0.104821,0.0322679,1.40244
2000,0.121979,0.152078,0.0693151,0.0191165
"""
        self.extract_range_api = StringIO(self.extract_range.decode())

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
        assert_frame_equal(out, otherout, check_dtype=False)

    def test_extract_one_label_labelstr_api(self):
        out = hspfbintoolbox.extract("tests/data_yearly.hbn", "yearly", ",905,,AGWS")
        otherout = tsutils.asbestfreq(
            pd.read_csv(self.extract_api, header=0, index_col=0, parse_dates=True)
        )
        otherout.index = otherout.index.to_period()
        assert_frame_equal(out, otherout, check_dtype=False)

    def test_extract_range_label_cli(self):
        args = "hspfbintoolbox extract tests/data_yearly.hbn yearly ,901:903+905,,AGWS"
        args = shlex.split(args)
        out = subprocess.Popen(
            args, stdout=subprocess.PIPE, stdin=subprocess.PIPE
        ).communicate()[0]
        self.assertEqual(out, self.extract_range)

    def test_extract_range_label_labellist_api(self):
        out = hspfbintoolbox.extract(
            "tests/data_yearly.hbn", "yearly", ["", "901:903+905", "", "AGWS"]
        )
        otherout = tsutils.asbestfreq(
            pd.read_csv(self.extract_range_api, header=0, index_col=0, parse_dates=True)
        )
        otherout.index = otherout.index.to_period()
        assert_frame_equal(out, otherout, check_dtype=False)

    def test_extract_range_label_labelstr_api(self):
        out = hspfbintoolbox.extract(
            "tests/data_yearly.hbn", "yearly", ",901:903+905,,AGWS"
        )
        otherout = tsutils.asbestfreq(
            pd.read_csv(self.extract_range_api, header=0, index_col=0, parse_dates=True)
        )
        otherout.index = otherout.index.to_period()
        assert_frame_equal(out, otherout, check_dtype=False)
