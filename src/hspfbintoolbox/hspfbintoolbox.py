"""
hspfbintoolbox to read HSPF binary files.
"""

import os
import sys
from typing import Literal

import pandas as pd

try:
    from pydantic import validate_call
except ImportError:
    from pydantic import validate_arguments as validate_call

from hspfbintoolbox.toolbox_utils.src.toolbox_utils import tsutils
from hspfbintoolbox.toolbox_utils.src.toolbox_utils.readers.hbn import _get_data

code2intervalmap = {5: "yearly", 4: "monthly", 3: "daily", 2: "bivl"}

interval2codemap = {"yearly": 5, "monthly": 4, "daily": 3, "bivl": 2}

pd_version = [int(i) for i in pd.__version__.split(".")[:2]]
if pd_version < [2, 2]:
    code2freqmap = {5: "A", 4: "M", 3: "D", 2: None}
else:
    code2freqmap = {5: "Y", 4: "M", 3: "D", 2: None}

_LOCAL_DOCSTRINGS = {
    "hbnfilename": r"""hbnfilename: str
        The HSPF binary output file.  This file must have been created from
        a completed model run."""
}

tablefmt_docstring = (
    """[optional, default is 'cvs_nos']

The table format.  Can be one of 'csv', 'tsv', 'csv_nos', 'tsv_nos',
'plain', 'simple', 'github', 'grid', 'fancy_grid', 'pipe', 'orgtbl',
'jira', 'presto', 'psql', 'rst', 'mediawiki', 'moinmoin', 'youtrack',
'html', 'latex', 'latex_raw', 'latex_booktabs' and 'textile'.""",
)
float_format_docstring = (
    """[optional, default is 'g']

The format for floating point numbers in the output table.""",
)


@validate_call
@tsutils.doc({**tsutils.docstrings, **_LOCAL_DOCSTRINGS})
def extract(
    hbnfilename: str,
    interval: Literal["yearly", "monthly", "daily", "bivl"],
    *labels,
    start_date=None,
    end_date=None,
    sort_columns: bool = False,
):
    """
    Extracts data from a HSPF binary output file.

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

        Examples::

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
    columns = [f"{i[0]}_{i[1]}_{i[3]}".replace(" ", "-") for i in skeys]
    result = pd.DataFrame(
        pd.concat(
            [pd.Series(data[i], index=index) for i in skeys], sort=False, axis=1
        ).reindex(pd.Index(index))
    )
    result.columns = columns
    result = tsutils.asbestfreq(result)
    result = tsutils.common_kwds(result, start_date=start_date, end_date=end_date)
    if interval == "bivl":
        result.index = result.index.to_period(result.index[1] - result.index[0])
    else:
        result.index = result.index.to_period()
    result.index.name = "Datetime"

    return result


@validate_call
@tsutils.doc({**tsutils.docstrings, **_LOCAL_DOCSTRINGS})
def catalog(hbnfilename: str):
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
    # PERLND  905  PWATER  SURS  5  1951  2001  yearly
    # PERLND  905  PWATER  TAET  5  1951  2001  yearly
    catlog = _get_data(hbnfilename, None, [",,,"], catalog_only=True)[1]
    catkeys = sorted(catlog.keys())
    return [cat + catlog[cat] + (code2intervalmap[cat[-1]],) for cat in catkeys]


def about():
    """Display version number and system information."""
    tsutils.about(__name__)


def main():
    if not os.path.exists("debug_hspfbintoolbox"):
        sys.tracebacklimit = 0

    from argparse import RawTextHelpFormatter

    import cltoolbox

    @cltoolbox.command("about", formatter_class=RawTextHelpFormatter)
    @tsutils.copy_doc(about)
    def about_cli():
        import pprint

        pprint.pprint(tsutils.about(__name__))

    @cltoolbox.command("extract", formatter_class=RawTextHelpFormatter)
    @cltoolbox.arg("tablefmt", help=tablefmt_docstring)
    @cltoolbox.arg("float_format", help=float_format_docstring)
    @tsutils.copy_doc(extract)
    def _extract_cli(
        hbnfilename,
        interval,
        start_date=None,
        end_date=None,
        sort_columns=False,
        tablefmt="csv_nos",
        float_format="g",
        *labels,
    ):
        tsutils.printiso(
            extract(
                hbnfilename,
                interval,
                *labels,
                start_date=start_date,
                end_date=end_date,
                sort_columns=sort_columns,
            ),
            tablefmt=tablefmt,
            float_format=float_format,
        )

    @cltoolbox.command("catalog", formatter_class=RawTextHelpFormatter)
    @cltoolbox.arg("tablefmt", help=tablefmt_docstring)
    @cltoolbox.arg("float_format", help=float_format_docstring)
    @tsutils.copy_doc(catalog)
    def _catalog_cli(
        hbnfilename,
        header="default",
        tablefmt="csv_nos",
        float_format="g",
    ):
        if header == "default":
            header = ["LUE", "LC", "GROUP", "VAR", "TC", "START", "END", "TC"]
        tsutils.printiso(
            catalog(hbnfilename),
            headers=header,
            showindex=False,
            tablefmt=tablefmt,
            float_format=float_format,
        )

    cltoolbox.main()


if __name__ == "__main__":
    main()
