# -*- coding: utf-8 -*-
"""
hspfbintoolbox to read HSPF binary files.
"""

from __future__ import print_function

import datetime
import os
import struct
import sys
import warnings

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import mando
import pandas as pd
import typic
from mando.rst_text_formatter import RSTHelpFormatter
from tstoolbox import tsutils

code2intervalmap = {5: "yearly", 4: "monthly", 3: "daily", 2: "bivl"}

interval2codemap = {"yearly": 5, "monthly": 4, "daily": 3, "bivl": 2}

code2freqmap = {5: "A", 4: "M", 3: "D", 2: None}


_LOCAL_DOCSTRINGS = {
    "hbnfilename": r"""hbnfilename: str
        The HSPF binary output file.  This file must have been created from
        a completed model run."""
}


def tupleMatch(a, b):
    """Part of partial ordered matching.
    See http://stackoverflow.com/a/4559604
    """
    return len(a) == len(b) and all(
        i is None or j is None or i == j for i, j in zip(a, b)
    )


def tupleCombine(a, b):
    """Part of partial ordered matching.
    See http://stackoverflow.com/a/4559604
    """
    return tuple(i is None and j or i for i, j in zip(a, b))


def tupleSearch(findme, haystack):
    """Partial ordered matching with 'None' as wildcard
    See http://stackoverflow.com/a/4559604
    """
    return [
        (i, tupleCombine(findme, h))
        for i, h in enumerate(haystack)
        if tupleMatch(findme, h)
    ]


def _get_data(binfilename, interval="daily", labels=None, catalog_only=True):
    """Underlying function to read from the binary file.  Used by
    'extract', 'catalog', and 'dump'.
    """
    if labels is None:
        labels = [",,,"]
    testem = {
        "PERLND": [
            "ATEMP",
            "SNOW",
            "PWATER",
            "SEDMNT",
            "PSTEMP",
            "PWTGAS",
            "PQUAL",
            "MSTLAY",
            "PEST",
            "NITR",
            "PHOS",
            "TRACER",
            "",
        ],
        "IMPLND": ["ATEMP", "SNOW", "IWATER", "SOLIDS", "IWTGAS", "IQUAL", ""],
        "RCHRES": [
            "HYDR",
            "CONS",
            "HTRCH",
            "SEDTRN",
            "GQUAL",
            "OXRX",
            "NUTRX",
            "PLANK",
            "PHCARB",
            "INFLOW",
            "OFLOW",
            "ROFLOW",
            "",
        ],
        "BMPRAC": [""],
        "": [""],
    }

    collect_dict = {}
    lablist = []

    # Normalize interval code
    try:
        intervalcode = interval2codemap[interval.lower()]
    except AttributeError:
        intervalcode = None

    # Fixup and test the labels - could be in it's own function
    if isinstance(labels, str):
        labels = labels.split(" ")
    labels = tsutils.flatten(labels)
    for lindex, label in enumerate(labels):
        words = [lindex] + label.split(",")
        if len(words) != 5:
            raise ValueError(
                tsutils.error_wrapper(
                    """
The label '{}' has the wrong number of entries.
""".format(
                        label
                    )
                )
            )

        words = [None if i == "" else i for i in words]

        if words[1] is not None:
            words[1] = words[1].upper()
            if words[1] not in testem.keys():
                raise ValueError(
                    tsutils.error_wrapper(
                        """
Operation type must be one of 'PERLND', 'IMPLND', 'RCHRES', or 'BMPRAC',
or missing (to get all) instead of {}.
""".format(
                            words[1]
                        )
                    )
                )

        if words[2] is not None:
            try:
                words[2] = int(words[2])
                if words[2] < 1 or words[2] > 999:
                    raise ValueError()
            except (ValueError, TypeError):
                raise ValueError(
                    tsutils.error_wrapper(
                        """
The land use element must be an integer from 1 to 999 inclusive,
instead of {}.
""".format(
                            words[2]
                        )
                    )
                )

        if words[3] is not None:
            words[3] = words[3].upper()
            if words[3] not in testem[words[1]]:
                raise ValueError(
                    tsutils.error_wrapper(
                        """
The {} operation type only allows the variable groups:
{},
instead you gave {}.
""".format(
                            words[1], testem[words[1]][:-1], words[3]
                        )
                    )
                )

        words.append(intervalcode)
        lablist.append(words)

    with open(binfilename, "rb") as fl:

        mindate = datetime.datetime.max
        maxdate = datetime.datetime.min

        labeltest = {}
        vnames = {}
        ndates = {}
        rectype = 0
        fl.read(1)
        while True:
            try:
                reclen1, reclen2, reclen3, reclen = struct.unpack("4B", fl.read(4))
            except struct.error:
                # End of file.
                break

            rectype, optype, lue, section = struct.unpack("I8sI8s", fl.read(24))

            rectype = int(rectype)
            lue = int(lue)
            optype = optype.strip()
            section = section.strip()

            slen = 0
            if rectype == 0:
                reclen1 = int(reclen1 / 4)
                reclen2 = reclen2 * 64 + reclen1
                reclen3 = reclen3 * 16384 + reclen2
                reclen = reclen * 4194304 + reclen3 - 24
                while slen < reclen:
                    length = struct.unpack("I", fl.read(4))[0]
                    slen = slen + length + 4
                    variable_name = struct.unpack(
                        "{}s".format(length), fl.read(length)
                    )[0]
                    vnames.setdefault((lue, section), []).append(variable_name)

            elif rectype == 1:
                # Data record
                numvals = len(vnames[(lue, section)])

                (_, level, year, month, day, hour, minute) = struct.unpack(
                    "7I", fl.read(28)
                )

                vals = struct.unpack("{}f".format(numvals), fl.read(4 * numvals))
                if hour == 24:
                    ndate = (
                        datetime.datetime(year, month, day)
                        + datetime.timedelta(hours=24)
                        + datetime.timedelta(minutes=minute)
                    )
                else:
                    ndate = datetime.datetime(year, month, day, hour, minute)

                for i, vname in enumerate(vnames[(lue, section)]):
                    tmpkey = (
                        None,
                        optype.decode("ascii"),
                        int(lue),
                        section.decode("ascii"),
                        vname.decode("ascii"),
                        level,
                    )
                    if catalog_only is False:
                        res = tupleSearch(tmpkey, lablist)
                        if res:
                            nres = (res[0][0],) + res[0][1][1:]
                            labeltest[nres[0]] = 1
                            collect_dict.setdefault(nres, []).append(vals[i])
                            ndates.setdefault(level, {})[ndate] = 1
                    else:
                        mindate = min(mindate, ndate)
                        maxdate = max(maxdate, ndate)
                        pdoffset = code2freqmap[level]
                        collect_dict[tmpkey[1:]] = (
                            pd.Period(mindate, freq=pdoffset),
                            pd.Period(maxdate, freq=pdoffset),
                        )
            else:
                fl.seek(-31, 1)

            # The following should be 1 or 2, but I don't know how to calculate
            # it, so I just use that the 'rectype' must be 0 or 1, and if not
            # rewind the correct amount.
            fl.read(2)

    if not collect_dict:
        raise ValueError(
            tsutils.error_wrapper(
                """
The label specifications below matched no records in the binary file.

{lablist}
""".format(
                    **locals()
                )
            )
        )

    if catalog_only is False:
        not_in_file = []
        for loopcnt in list(range(len(lablist))):
            if loopcnt not in labeltest.keys():
                not_in_file.append(labels[loopcnt])
        if not_in_file:
            warnings.warn(
                tsutils.error_wrapper(
                    """
The specification{} {}
matched no records in the binary file.
""".format(
                        "s"[len(not_in_file) == 1 :], not_in_file
                    )
                )
            )

    return ndates, collect_dict


@mando.command("extract", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.merge_dicts(tsutils.docstrings, _LOCAL_DOCSTRINGS))
def extract_cli(hbnfilename, interval, *labels, **kwds):
    r"""Prints out data to the screen from a HSPF binary output file.

    Parameters
    ----------
    ${hbnfilename}

    interval: str
        One of 'yearly', 'monthly', 'daily', or 'BIVL'.  The 'BIVL' option is
        a sub-daily interval defined in the UCI file.  Typically 'BIVL' is used
        for hourly output, but can be set to any value that evenly divides into
        a day.

    labels: str
        The remaining arguments uniquely identify a time-series in the
        binary file.  The format is 'OPERATIONTYPE,ID,VARIABLE_GROUP,VARIABLE'.

        For example: 'PERLND,101,PWATER,UZS IMPLND,101,IWATER,RETS'

        Leaving a section without an entry will wildcard that
        specification.  To get all the PWATER variables for PERLND 101 the
        label would read:

        'PERLND,101,PWATER,'

        To get TAET for all PERLNDs:

        'PERLND,,,TAET'

        Note that there are spaces ONLY between label specifications.

        OPERATIONTYE can be PERLND, IMPLND, RCHRES, and BMPRAC.

        ID is specified in the UCI file.

        VARIABLE_GROUP depends on OPERATIONTYPE where::

            if OPERATIONTYPE is PERLND then VARIABLEGROUP can be one of
                'ATEMP', 'SNOW', 'PWATER', 'SEDMNT', 'PSTEMP', 'PWTGAS',
                'PQUAL', 'MSTLAY', 'PEST', 'NITR', 'PHOS', 'TRACER'

            if OPERATIONTYPE is IMPLND then VARIABLEGROUP can be one of
                'ATEMP', 'SNOW', 'IWATER', 'SOLIDS', 'IWTGAS', 'IQUAL'

            if OPERATIONTYPE is RCHRES then VARIABLEGROUP can be one of
                'HYDR', 'CONS', 'HTRCH', 'SEDTRN', 'GQUAL', 'OXRX', 'NUTRX',
                'PLANK', 'PHCARB', 'INFLOW', 'OFLOW', 'ROFLOW'

            if OPERATIONTYPE is BMPRAC then there is no VARIABLEGROUP and you
            have to leave VARIABLEGROUP as a wild card.  For example,
            'BMPRAC,875,,RMVOL'.

    kwds:
        Current the allowable keywords are 'time_stamp' and
        'sorted'.

        time_stamp:
        [optional, default is 'begin']

        For the interval defines the location of the time stamp. If set to
        'begin', the time stamp is at the beginning of the interval.  If set to
        any other string, the reported time stamp will represent the end of the
        interval.  Place after ALL labels.

        sorted:
        [optional, default is False]

        Should ALL columns be sorted?  Place after ALL labels."""
    tsutils._printiso(extract(hbnfilename, interval, *labels, **kwds))


@typic.al
def extract(
    hbnfilename: str,
    interval: Literal["yearly", "monthly", "daily", "BIVL"],
    *labels,
    **kwds
):
    r"""Returns a DataFrame from a HSPF binary output file."""
    try:
        time_stamp = kwds.pop("time_stamp")
    except KeyError:
        time_stamp = "begin"
    if time_stamp not in ["begin", "end"]:
        raise ValueError(
            tsutils.error_wrapper(
                """
The "time_stamp" optional keyword must be either
"begin" or "end".  You gave {}.
""".format(
                    time_stamp
                )
            )
        )

    try:
        sortall = bool(kwds.pop("sorted"))
    except KeyError:
        sortall = False
    if not (sortall is True or sortall is False):
        raise ValueError(
            tsutils.error_wrapper(
                """
The "sorted" optional keyword must be either
True or False.  You gave {}.
""".format(
                    sortall
                )
            )
        )

    if len(kwds) > 0:
        raise ValueError(
            tsutils.error_wrapper(
                """
The extract command only accepts optional keywords 'time_stamp' and
'sorted'.  You gave {}.
""".format(
                    list(kwds.keys())
                )
            )
        )

    interval = interval.lower()
    if interval not in ["bivl", "daily", "monthly", "yearly"]:
        raise ValueError(
            tsutils.error_wrapper(
                """
The "interval" argument must be one of "bivl",
"daily", "monthly", or "yearly".  You supplied
"{}".
""".format(
                    interval
                )
            )
        )

    index, data = _get_data(hbnfilename, interval, labels, catalog_only=False)
    index = index[interval2codemap[interval]]
    index = sorted(index.keys())
    skeys = list(data.keys())
    if sortall is True:
        skeys.sort(key=lambda tup: tup[1:])
    else:
        skeys.sort()

    result = pd.DataFrame(
        pd.concat(
            [pd.Series(data[i], index=index) for i in skeys], sort=False, axis=1
        ).reindex(pd.Index(index))
    )
    columns = ["{}_{}_{}_{}".format(i[1], i[2], i[4], i[5]) for i in skeys]
    result.columns = columns

    if time_stamp == "begin":
        result = tsutils.asbestfreq(result)
        result = result.shift(-1, freq="infer")

    result.index.name = "Datetime"

    return result


@mando.command("catalog", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.merge_dicts(tsutils.docstrings, _LOCAL_DOCSTRINGS))
def catalog_cli(hbnfilename, tablefmt="simple", header="default"):
    """
    Prints out a catalog of data sets in the binary file.

    The first four items of each line can be used as labels with the 'extract'
    command to identify time-series in the binary file.

    Parameters
    ----------
    ${hbnfilename}
    ${tablefmt}
    ${header}

    """
    if header == "default":
        header = ["LUE", "LC", "GROUP", "VAR", "TC", "START", "END", "TC"]
    tsutils._printiso(catalog(hbnfilename), tablefmt=tablefmt, headers=header)


@typic.al
def catalog(hbnfilename: str):
    """
    Prints out a catalog of data sets in the binary file.
    """
    # PERLND  905  PWATER  SURS  5  1951  2001  yearly
    # PERLND  905  PWATER  TAET  5  1951  2001  yearly
    catlog = _get_data(hbnfilename, None, [",,,"], catalog_only=True)[1]
    catkeys = sorted(catlog.keys())
    result = []
    for cat in catkeys:
        result.append(cat + catlog[cat] + (code2intervalmap[cat[-1]],))
    return result


@mando.command("dump", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.merge_dicts(tsutils.docstrings, _LOCAL_DOCSTRINGS))
def dump_cli(hbnfilename, time_stamp="begin"):
    """
    Prints out ALL data from a HSPF binary output file.

    Parameters
    ----------
    ${hbnfilename}

    time_stamp
        [optional, default is 'begin']

        For the interval defines the location of the time stamp. If set
        to 'begin', the time stamp is at the begining of the interval.
        If set to any other string, the reported time stamp will
        represent the end of the interval.  Default is 'begin'.Z

    """
    tsutils._printiso(dump(hbnfilename, time_stamp=time_stamp))


@typic.al
def dump(hbnfilename: str, time_stamp: Literal["begin", "end"] = "begin"):
    """
    Prints out ALL data from a HSPF binary output file.
    """
    if time_stamp not in ["begin", "end"]:
        raise ValueError(
            tsutils.error_wrapper(
                """
The "time_stamp" optional keyword must be either
"begin" or "end".  You gave {}.
""".format(
                    time_stamp
                )
            )
        )

    index, data = _get_data(hbnfilename, None, [",,,"], catalog_only=False)
    skeys = sorted(data.keys())

    result = pd.DataFrame(
        pd.concat(
            [pd.Series(data[i], index=index) for i in skeys], sort=False, axis=1
        ).reindex(pd.Index(index))
    )

    columns = ["{}_{}_{}_{}".format(i[1], i[2], i[4], i[5]) for i in skeys]
    result.columns = columns

    if time_stamp == "begin":
        result = tsutils.asbestfreq(result)
        result = result.shift(-1, freq="infer")

    return result


@mando.command()
def about():
    """Display version number and system information."""
    tsutils.about(__name__)


@mando.command
def time_series(hbnfilename, interval, *labels, **kwds):
    """DEPRECATED: Use 'extract' instead."""
    return extract(hbnfilename, interval, *labels, **kwds)


def main():
    if not os.path.exists("debug_hspfbintoolbox"):
        sys.tracebacklimit = 0
    mando.main()


if __name__ == "__main__":
    main()
