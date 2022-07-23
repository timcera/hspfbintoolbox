# -*- coding: utf-8 -*-
"""
hspfbintoolbox to read HSPF binary files.
"""


import datetime
import os
import struct
import sys

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import cltoolbox
import pandas as pd
import typic
from cltoolbox.rst_text_formatter import RSTHelpFormatter
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
    'extract', 'catalog'.
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

    # Fix up and test the labels - could be in it's own function
    if isinstance(labels, str):
        labels = labels.split(" ")
    labels = tsutils.flatten(labels)
    nlabels = []
    for label in labels:
        if isinstance(label, str):
            nlabels.append(label.split(","))
        else:
            nlabels.append(label)
    labels = tsutils.flatten(nlabels)
    labels = [[a, b, c, d] for a, b, c, d in zip(*[iter(labels)] * 4)]

    for label in labels:
        words = label
        if len(words) != 4:
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
The label '{label}' has the wrong number of entries.
"""
                )
            )

        words = [None if i == "" else i for i in words]

        if words[0] is not None:
            words[0] = words[0].upper()
            if words[0] not in testem.keys():
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
Operation type must be one of 'PERLND', 'IMPLND', 'RCHRES', or 'BMPRAC',
or missing (to get all) instead of {words[0]}.
"""
                    )
                )

        if words[1] is not None:
            try:
                words[1] = int(words[1])
                if words[1] < 1 or words[1] > 999:
                    raise ValueError()
            except (ValueError, TypeError):
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
The land use element must be an integer from 1 to 999 inclusive,
instead of {words[1]}.
"""
                    )
                )

        if words[2] is not None:
            words[2] = words[2].upper()
            if words[2] not in testem[words[0]]:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
The {words[0]} operation type only allows the variable groups:
{testem[words[0]][:-1]},
instead you gave {words[2]}.
"""
                    )
                )

        words.append(intervalcode)
        lablist.append(words)

    with open(binfilename, "rb") as fl:

        mindate = datetime.datetime.max
        maxdate = datetime.datetime.min

        labeltest = set()
        vnames = {}
        ndates = set()
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
                    variable_name = struct.unpack(f"{length}s", fl.read(length))[0]
                    vnames.setdefault((lue, section), []).append(variable_name)

            elif rectype == 1:
                # Data record
                numvals = len(vnames[(lue, section)])

                (_, level, year, month, day, hour, minute) = struct.unpack(
                    "7I", fl.read(28)
                )

                vals = struct.unpack(f"{numvals}f", fl.read(4 * numvals))

                delta = datetime.timedelta(hours=0)
                if hour == 24:
                    hour = 0
                    # if intervalcode == 2:
                    #    delta = datetime.timedelta(hours=24)

                ndate = datetime.datetime(year, month, day, hour, minute) + delta

                for i, vname in enumerate(vnames[(lue, section)]):
                    tmpkey = (
                        optype.decode("ascii"),
                        lue,
                        section.decode("ascii"),
                        vname.decode("ascii"),
                        level,
                    )

                    for lb in lablist:
                        res = tupleSearch(tmpkey, [lb])
                        if not res:
                            continue
                        labeltest.add(tuple(lb))
                        nres = res[0][1]
                        ndates.add(ndate)
                        if catalog_only is False:
                            if intervalcode == level:
                                collect_dict.setdefault(nres, []).append(vals[i])
                        else:
                            collect_dict[nres] = level
            else:
                fl.seek(-31, 1)

            # The following should be 1 or 2, but I don't know how to calculate
            # it, so I just use that the next value read is 'rectype' which
            # must be 0 or 1, and if not means that the fl.read(2) should have
            # been fl.read(1) and rewind the correct amount.  This is a hack,
            # but it works. This is done at the beginning of the loop, so it
            # should be fine.
            fl.read(2)

    if not collect_dict:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
The label specifications below matched no records in the binary file.

{lablist}
"""
            )
        )

    ndates = sorted(list(ndates))

    if catalog_only is False:
        for lb in lablist:
            if tuple(lb) not in labeltest:
                sys.stderr.write(
                    tsutils.error_wrapper(
                        f"""
Warning: The label '{lb}' matched no records in the binary file.
"""
                    )
                )
    else:
        for key in collect_dict:
            if key[4] == 2:
                delta = ndates[1] - ndates[0]
            else:
                delta = code2freqmap[key[4]]
            collect_dict[key] = (
                pd.Period(ndates[0], freq=delta),
                pd.Period(ndates[-1], freq=delta),
            )

    return ndates, collect_dict


@cltoolbox.command("extract", formatter_class=RSTHelpFormatter)
@tsutils.doc(tsutils.merge_dicts(tsutils.docstrings, _LOCAL_DOCSTRINGS))
def extract_cli(
    hbnfilename, interval, start_date=None, end_date=None, sort_columns=False, *labels
):
    r"""Prints out data to the screen from a HSPF binary output file.

    Parameters
    ----------
    ${hbnfilename}

    interval: str
        One of 'yearly', 'monthly', 'daily', or 'bivl'.  The 'bivl' option is
        a sub-daily interval defined in the UCI file.  Typically 'bivl' is used
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

    ${start_date}
    ${end_date}
    sort_columns:
        [optional, default is False]

        If set to False will maintain the columns order of the labels.  If set
        to True will sort all columns by their columns names."""
    tsutils.printiso(
        extract(
            hbnfilename,
            interval,
            *labels,
            start_date=start_date,
            end_date=end_date,
            sort_columns=sort_columns,
        )
    )


@typic.al
def extract(
    hbnfilename: str,
    interval: Literal["yearly", "monthly", "daily", "bivl"],
    *labels,
    start_date=None,
    end_date=None,
    sort_columns: bool = False,
):
    r"""Returns a DataFrame from a HSPF binary output file."""
    interval = interval.lower()
    if interval not in ["bivl", "daily", "monthly", "yearly"]:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
The "interval" argument must be one of "bivl",
"daily", "monthly", or "yearly".  You supplied
"{interval}".
"""
            )
        )

    index, data = _get_data(hbnfilename, interval, labels, catalog_only=False)
    index = sorted(list(index))
    skeys = list(data.keys())
    if sort_columns:
        skeys.sort(key=lambda tup: tup[1:])
    else:
        skeys.sort()

    result = pd.DataFrame(
        pd.concat(
            [pd.Series(data[i], index=index) for i in skeys], sort=False, axis=1
        ).reindex(pd.Index(index))
    )
    columns = [f"{i[0]}_{i[1]}_{i[3]}".replace(" ", "-") for i in skeys]
    result.columns = columns
    result = tsutils.asbestfreq(result)
    if start_date is not None or end_date is not None:
        result = tsutils.common_kwds(result, start_date=start_date, end_date=end_date)
    if interval == "bivl":
        result.index = result.index.to_period(result.index[1] - result.index[0])
    else:
        result.index = result.index.to_period()
    result.index.name = "Datetime"

    return result


@cltoolbox.command("catalog", formatter_class=RSTHelpFormatter)
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
    tsutils.printiso(catalog(hbnfilename), tablefmt=tablefmt, headers=header)


@typic.al
def catalog(hbnfilename: str):
    """
    Prints out a catalog of data sets in the binary file.
    """
    # PERLND  905  PWATER  SURS  5  1951  2001  yearly
    # PERLND  905  PWATER  TAET  5  1951  2001  yearly
    catlog = _get_data(hbnfilename, None, [",,,"], catalog_only=True)[1]
    catkeys = sorted(catlog.keys())
    return [cat + catlog[cat] + (code2intervalmap[cat[-1]],) for cat in catkeys]


@cltoolbox.command()
def about():
    """Display version number and system information."""
    tsutils.about(__name__)


def main():
    if not os.path.exists("debug_hspfbintoolbox"):
        sys.tracebacklimit = 0
    if os.path.exists("profile_hspfbintoolbox"):
        import functiontrace

        functiontrace.trace()
    cltoolbox.main()


if __name__ == "__main__":
    main()
