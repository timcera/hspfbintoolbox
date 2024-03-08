"""
hspfbintoolbox to read HSPF binary files.
"""

import datetime
import os
import struct
import sys
from typing import Literal

import pandas as pd
from cltoolbox import Program
from cltoolbox.rst_text_formatter import RSTHelpFormatter

try:
    from pydantic import validate_call
except ImportError:
    from pydantic import validate_arguments as validate_call

from toolbox_utils import tsutils

program = Program("hspfbintoolbox", 0.0)

code2intervalmap = {5: "yearly", 4: "monthly", 3: "daily", 2: "bivl"}

interval2codemap = {"yearly": 5, "monthly": 4, "daily": 3, "bivl": 2}

code2freqmap = {5: "A", 4: "M", 3: "D", 2: None}


_LOCAL_DOCSTRINGS = {
    "hbnfilename": r"""hbnfilename: str
        The HSPF binary output file.  This file must have been created from
        a completed model run."""
}


def tuple_match(a, b):
    """Part of partial ordered matching.
    See http://stackoverflow.com/a/4559604
    """
    return len(a) == len(b) and all(
        i is None or j is None or i == j for i, j in zip(a, b)
    )


def tuple_combine(a, b):
    """Part of partial ordered matching.
    See http://stackoverflow.com/a/4559604
    """
    return tuple(i is None and j or i for i, j in zip(a, b))


def tuple_search(findme, haystack):
    """Partial ordered matching with 'None' as wildcard
    See http://stackoverflow.com/a/4559604
    """
    return [
        (i, tuple_combine(findme, h))
        for i, h in enumerate(haystack)
        if tuple_match(findme, h)
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

    # convert label tuples to lists
    labels = list(labels)

    # turn into a list of lists
    nlabels = []
    for label in labels:
        if isinstance(label, str):
            nlabels.append(label.split(","))
        else:
            nlabels.append(label)
    labels = nlabels

    # Check the list members for valid values
    for label in labels:
        if len(label) != 4:
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
                    The label '{label}' has the wrong number of entries.
                    """
                )
            )

        # replace empty fields with None
        words = [None if i == "" else i for i in label]

        # first word must be a valid operation type or None
        if words[0] is not None:
            # force uppercase before comparison
            words[0] = words[0].upper()
            if words[0] not in testem:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        Operation type must be one of 'PERLND', 'IMPLND',
                        'RCHRES', or 'BMPRAC', or missing (to get all) instead
                        of {words[0]}.
                        """
                    )
                )

        # second word must be integer 1-999 or None or range to parse
        if words[1] is not None:
            try:
                words[1] = int(words[1])
                luelist = [words[1]]
            except ValueError:
                luelist = tsutils.range_to_numlist(words[1])
            for luenum in luelist:
                if luenum < 1 or luenum > 999:
                    raise ValueError(
                        tsutils.error_wrapper(
                            f"""
                            The land use element must be an integer from 1 to
                            999 inclusive, instead of {luenum}.
                            """
                        )
                    )
        else:
            luelist = [None]

        # third word must be a valid group name or None
        if words[2] is not None:
            words[2] = words[2].upper()
            if words[2] not in testem[words[0]]:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        The {words[0]} operation type only allows the variable
                        groups: {testem[words[0]][:-1]},
                        instead you gave {words[2]}.
                        """
                    )
                )

        # fourth word is currently not checked - assumed to be a variable name
        # if not, it will simply never be found in the file, so ok
        # but no warning for the user - add check?

        # add interval code as fifth word in list
        words.append(intervalcode)

        # add to new list of checked and expanded lists
        for luenum in luelist:
            words[1] = luenum
            lablist.append(list(words))

    # Now read through the binary file and collect the data matching the labels
    with open(binfilename, "rb") as binfp:
        labeltest = set()
        vnames = {}
        ndates = set()
        # read first byte - must be hex FD (decimal 253) for valid file.
        magicbyte = binfp.read(1)
        if magicbyte != b"\xfd":
            # not a valid HSPF binary file
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
                    {binfilename} is not a valid HSPF binary output file
                    (.hbn),  The first byte must be FD hexadecimal, but it was
                    {magicbyte}.
                    """
                )
            )

        # loop through each record
        while True:
            # reinitialize counter for record length - used to compute skip at
            # end
            recpos = 0

            # read first four bytes to get record length bitfield
            try:
                reclen1, reclen2, reclen3, reclen = struct.unpack("4B", binfp.read(4))
                recpos += 4
            except struct.error:
                # End of file.
                break

            # get record leader - next 24 bytes
            rectype, optype, lue, group = struct.unpack("I8sI8s", binfp.read(24))
            recpos += 24

            # clean up
            rectype = int(rectype)
            lue = int(lue)
            optype = optype.strip()
            group = group.strip()

            if rectype == 0:
                # header record - collect variable names for this
                # operation and group

                # parse reclen bitfield to get actual remaining length
                # the " - 24 " subtracts the 24 bytes already read
                reclen1 = int(reclen1 / 4)
                reclen2 = reclen2 * 64 + reclen1
                reclen3 = reclen3 * 16384 + reclen2
                reclen = reclen * 4194304 + reclen3 - 24

                # loop through rest of record
                slen = 0
                while slen < reclen:
                    # read single 4B word for length of next variable name
                    length = struct.unpack("I", binfp.read(4))[0]

                    # read the variable name
                    variable_name = struct.unpack(f"{length}s", binfp.read(length))[0]

                    # add variable name to the set for this operation
                    # why a set instead of a list? There should never be
                    # a duplicate anyway
                    vnames.setdefault((lue, group), []).append(variable_name)

                    # update how far along the record we are
                    slen += length + 4
                    recpos += length + 4

            elif rectype == 1:
                # Data record

                # record should contain a value for each variable name for this
                # operation and group
                numvals = len(vnames[(lue, group)])

                (_, level, year, month, day, hour, minute) = struct.unpack(
                    "7I", binfp.read(28)
                )
                recpos += 28

                vals = struct.unpack(f"{numvals}f", binfp.read(4 * numvals))
                recpos += 4 * numvals

                delta = datetime.timedelta(hours=0)
                if hour == 24:
                    hour = 0

                ndate = datetime.datetime(year, month, day, hour, minute) + delta

                #  Go through labels to see if these values need to be
                #  collected
                for i, vname in enumerate(vnames[(lue, group)]):
                    tmpkey = (
                        optype.decode("ascii"),
                        lue,
                        group.decode("ascii"),
                        vname.decode("ascii"),
                        level,
                    )

                    for lbl in lablist:
                        res = tuple_search(tmpkey, [lbl])
                        if not res:
                            continue
                        labeltest.add(tuple(lbl))
                        nres = res[0][1]
                        ndates.add(ndate)
                        if catalog_only is False:
                            if intervalcode == level:
                                collect_dict.setdefault(nres, []).append(vals[i])
                        else:
                            collect_dict[nres] = level
            else:
                # there was a problem with unexpected record length
                # back up almost all the way and try again
                binfp.seek(-31, 1)

            # calculate and skip to the end of the variable-length back pointer
            reccnt = recpos * 4 + 1
            if reccnt >= 256**2:
                skbytes = 3
            elif reccnt >= 256:
                skbytes = 2
            else:
                skbytes = 1
            binfp.read(skbytes)

    if not collect_dict:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                The label specifications below matched no records in the binary
                file.

                {lablist}
                """
            )
        )

    ndates = sorted(list(ndates))

    if catalog_only is False:
        for lbl in lablist:
            if tuple(lbl) not in labeltest:
                sys.stderr.write(
                    tsutils.error_wrapper(
                        f"""
                        Warning: The label '{lbl}' matched no records in the
                        binary file.
                        """
                    )
                )
    else:
        for key in collect_dict:
            delta = ndates[1] - ndates[0] if key[4] == 2 else code2freqmap[key[4]]
            collect_dict[key] = (
                pd.Period(ndates[0], freq=delta),
                pd.Period(ndates[-1], freq=delta),
            )

    return ndates, collect_dict


@program.command("extract", formatter_class=RSTHelpFormatter)
@tsutils.doc({**tsutils.docstrings, **_LOCAL_DOCSTRINGS})
def _extract_cli(
    hbnfilename, interval, start_date=None, end_date=None, sort_columns=False, *labels
):
    r"""Prints out data to the screen from a HSPF binary output file.

    Parameters
    ----------
    ${hbnfilename}

    interval : str
        One of 'yearly', 'monthly', 'daily', or 'bivl'.  The 'bivl' option is
        a sub-daily interval defined in the UCI file.  Typically 'bivl' is used
        for hourly output, but can be set to any value that evenly divides into
        a day.

    labels : str
        The remaining arguments uniquely identify a time-series in the
        binary file.  The format is 'OPERATIONTYPE,ID,VARIABLEGROUP,VARIABLE'.

        For example: 'PERLND,101,PWATER,UZS IMPLND,101,IWATER,RETS'

        Leaving a section without an entry will wild card that
        specification.  To get all the PWATER variables for PERLND 101 the
        label would read:

        'PERLND,101,PWATER,'

        To get TAET for all PERLNDs:

        'PERLND,,,TAET'

        Note that there are spaces ONLY between label specifications not within
        the labels themselves.

        OPERATIONTYE can be PERLND, IMPLND, RCHRES, and BMPRAC.

        ID is the operation type identification number specified in the UCI
        file. These numbers must be in the range 1-999.

        Here, the user can specify

            - a single ID number to match
            - no entry, matching any operation ID number
            - a range, specified as any combination of simple integers and
              groups of integers marked as "start:end", with multiple allowed
              sub-ranges separated by the "+" sign.

        Examples:

            +-----------------------+-------------------------------+
            | Label ID              | Expands to:                   |
            +=======================+===============================+
            | 1:10                  | 1,2,3,4,5,6,7,8,9,10          |
            +-----------------------+-------------------------------+
            | 101:119+221:239       | 101,102..119,221,221,...239   |
            +-----------------------+-------------------------------+
            | 3:5+7                 | 3,4,5,7                       |
            +-----------------------+-------------------------------+

        VARIABLEGROUP depends on OPERATIONTYPE where::

            if OPERATIONTYPE is PERLND then VARIABLEGROUP can be one of
                'ATEMP', 'SNOW', 'PWATER', 'SEDMNT', 'PSTEMP', 'PWTGAS',
                'PQUAL', 'MSTLAY', 'PEST', 'NITR', 'PHOS', 'TRACER'

            if OPERATIONTYPE is IMPLND then VARIABLEGROUP can be one of
                'ATEMP', 'SNOW', 'IWATER', 'SOLIDS', 'IWTGAS', 'IQUAL'

            if OPERATIONTYPE is RCHRES then VARIABLEGROUP can be one of
                'HYDR', 'CONS', 'HTRCH', 'SEDTRN', 'GQUAL', 'OXRX', 'NUTRX',
                'PLANK', 'PHCARB', 'INFLOW', 'OFLOW', 'ROFLOW'

            if OPERATIONTYPE is BMPRAC then VARIABLEGROUP is not used and you
            have to leave VARIABLEGROUP as a wild card.  For example,
            'BMPRAC,875,,RMVOL'.

        The Time Series Catalog in the HSPF Manual lists all of the variables
        in each of these VARIABLEGROUPs.  For BMPRAC, all of the variables in
        all Groups in the Catalog are available in the unnamed (blank) Group.

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


@validate_call
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
                The "interval" argument must be one of "bivl", "daily",
                "monthly", or "yearly".  You supplied "{interval}".
                """
            )
        )

    index, data = _get_data(hbnfilename, interval, labels, catalog_only=False)
    skeys = list(data.keys())
    if sort_columns:
        skeys.sort(key=lambda tup: tup[1:])

    result = pd.DataFrame(
        pd.concat(
            [pd.Series(data[i], index=index) for i in skeys], sort=False, axis=1
        ).reindex(pd.Index(index))
    )
    columns = [f"{i[0]}_{i[1]}_{i[3]}".replace(" ", "-") for i in skeys]
    result.columns = columns
    result = tsutils.asbestfreq(result)
    result = tsutils.common_kwds(result, start_date=start_date, end_date=end_date)
    if interval == "bivl":
        result.index = result.index.to_period(result.index[1] - result.index[0])
    else:
        result.index = result.index.to_period()
    result.index.name = "Datetime"

    return result


@program.command("catalog", formatter_class=RSTHelpFormatter)
@tsutils.doc({**tsutils.docstrings, **_LOCAL_DOCSTRINGS})
def _catalog_cli(hbnfilename, tablefmt="simple", header="default"):
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
    tsutils.printiso(
        catalog(hbnfilename), tablefmt=tablefmt, headers=header, showindex=False
    )


@validate_call
def catalog(hbnfilename: str):
    """
    Prints out a catalog of data sets in the binary file.
    """
    # PERLND  905  PWATER  SURS  5  1951  2001  yearly
    # PERLND  905  PWATER  TAET  5  1951  2001  yearly
    catlog = _get_data(hbnfilename, None, [",,,"], catalog_only=True)[1]
    catkeys = sorted(catlog.keys())
    return [cat + catlog[cat] + (code2intervalmap[cat[-1]],) for cat in catkeys]


@program.command()
def about():
    """Display version number and system information."""
    tsutils.about(__name__)


def main():
    if not os.path.exists("debug_hspfbintoolbox"):
        sys.tracebacklimit = 0
    if os.path.exists("profile_hspfbintoolbox"):
        import functiontrace

        functiontrace.trace()
    program()


if __name__ == "__main__":
    main()
