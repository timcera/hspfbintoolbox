# Example package with a console entry point

import datetime

from construct import *
import numpy as np
import baker
import pandas as pd

import tsutils


code2intervalmap = {5: 'yearly',
                    4: 'monthly',
                    3: 'daily',
                    2: 'bivl'}

interval2codemap = {'yearly': 5,
                    'monthly': 4,
                    'daily': 3,
                    'bivl': 2}

code2freqmap = {5: 'Y',
                4: 'M',
                3: 'D',
                2: None}

def _collect(binfilename):
    fl = open(binfilename, 'r').read()

    landuse_nos = []
    opertype = []
    variable_names = []
    levels = []
    values = []
    dates = []
    sections = []

    for optype in ['PERLND', 'IMPLND', 'RCHRES']:
        vnames = {}

        tindex = 0
        while 1:
            tindex = fl.find(optype, tindex + 1)
            if tindex == -1:
                break
            rectype = ULInt32("rectype").parse(fl[tindex - 4: tindex])
            lue = ULInt32("lue").parse(fl[tindex + 8: tindex + 12])
            slen = 20
            section = String("section", 8).parse(fl[tindex + 12: tindex + slen])
            if rectype == 0:
                reclen1 = int(ULInt8("reclen1").parse(fl[tindex - 8: tindex - 7]) / 4.0)
                reclen2 = ULInt8("reclen2").parse(fl[tindex - 7: tindex - 6])*64 + reclen1
                reclen3 = ULInt8("reclen3").parse(fl[tindex - 6: tindex - 5])*256*64 + reclen2
                reclen = ULInt8("reclen").parse(fl[tindex - 5: tindex - 4])*256**2*64 + reclen3
                # Header record
                while 1:
                    length = ULInt32("length").parse(fl[tindex + slen:
                                                        tindex + slen + 4])
                    variable_name = String("vars", length).parse(fl[tindex + slen + 4: tindex + slen + 4 + length])
                    vnames.setdefault((lue, section), []).append(variable_name)
                    if slen + 8 + length >= reclen:
                        break
                    slen = slen + 4 + length

            if rectype == 1:
                # Data record
                numvals = len(vnames[(lue, section)])
                unit_flag = ULInt32("unit_flag").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4
                level = ULInt32("level").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4
                year = ULInt32("year").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4
                month = ULInt32("month").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4
                day = ULInt32("day").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4
                hour = ULInt32("hour").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4
                minute = ULInt32("minute").parse(fl[tindex + slen: tindex + slen + 4])
                slen = slen + 4

                if hour == 24:
                    ndate = datetime.datetime(year, month, day) + datetime.timedelta(hours = 24) + datetime.timedelta(minutes = minute)
                else:
                    ndate = datetime.datetime(year, month, day, hour, minute)

                c = Array(numvals, LFloat32('PERVARS')).parse(fl[tindex + slen: tindex + slen + numvals*4])

                for varname, value in zip(vnames[(lue, section)], c):
                    opertype.append(optype)
                    landuse_nos.append(lue)
                    sections.append(section.strip())
                    variable_names.append(varname.strip())
                    levels.append(level)
                    dates.append(ndate)
                    values.append(value)

    index = pd.MultiIndex.from_arrays([
              np.array(opertype),
              np.array(landuse_nos),
              np.array(sections),
              np.array(variable_names),
              np.array(levels),
              np.array(dates)], names=['opertype', 'land_use', 'section',
                                       'variable_name', 'levels', 'Datetime'])

    return pd.DataFrame({'value': values}, index=index).sort()


def _catalog_data(ndata):
    cdata = zip(ndata.index.get_level_values('opertype'),
                ndata.index.get_level_values('land_use'),
                ndata.index.get_level_values('section'),
                ndata.index.get_level_values('variable_name'))
    return sorted(set(cdata))


@baker.command
def catalog(hbnfilename):
    ndata = _collect(hbnfilename)
    cdata = _catalog_data(ndata)
    try:
        for ot,lu,sec,vn in cdata:
            nrows = ndata.ix[ot,int(lu),sec,vn]
            levels = sorted(set(nrows.index.get_level_values('levels')))
            for lev in levels:
                nrows = ndata.ix[ot,int(lu),sec,vn,lev]
                maxdate = max(nrows.index)
                mindate = min(nrows.index)
                print '{0},{1},{2},{3}, {4}, {5}, {6}'.format(ot, lu, sec, vn, mindate,
                    maxdate, code2intervalmap[lev])
    except IOError:
        return


def _process_label_lists(ndata, llist):
    nlabels = []
    testlist = ['', '*']
    final_lab = []
    labdat = zip(ndata.index.get_level_values('opertype'),
                 ndata.index.get_level_values('land_use'),
                 ndata.index.get_level_values('section'),
                 ndata.index.get_level_values('variable_name'),
                 ndata.index.get_level_values('levels'))
    for label in llist:
        try:
            ot,lu,sec,vn,lev = label.split(',')
        except AttributeError:
            ot,lu,sec,vn,lev = label
        if lu in testlist:
            lu = ''
        else:
            lu = int(lu)
        lev = int(lev)

        # Test to see if any wildcards are in list...
        # If not just append label to final_lab
        wildcards = False
        for testl in testlist:
            if testl in [ot,lu,sec,vn,lev]:
                wildcards = True
        if not wildcards:
            if (ot,lu,sec,vn,lev) in labdat:
                final_lab.append((ot,lu,sec,vn,lev))
                continue
            else:
                raise ValueError('The specification "{0}" matched no records in the '
                                 'binary file'.format(label))

        # Handle wildcards...
        tmpdat = labdat
        for index,labpart in enumerate([ot,lu,sec,vn,lev]):
            if labpart not in testlist:
                tmpdat = [i for i in tmpdat if i[index] == labpart]
        if len(tmpdat) == 0:
            raise ValueError('The specification "{0}" matched no records in the '
                             'binary file'.format(label))
        final_lab = final_lab + tmpdat
    return sorted(set(final_lab))


def _collect_time_series(ndata, labels, time_stamp):
    '''
    Prints out data to the screen from a HSPF binary output file.
    :param hbnfilename: The HSPF binary output file
    :param interval: One of 'yearly', 'monthly', 'daily', or 'BIVL'.
        The 'BIVL' option is a sub-daily interval defined in the UCI file.
        Typically 'BIVL' is used for hourly output, but can be set to any
        value that evenly divides into a day.
    :param labels: The remaining arguments uniquely identify a time-series
        in the binary file.  The format is
        'OPERATIONTYPE,ID,SECTION,VARIABLE'.
        For example: PERLND,101,PWATER,UZS IMPLND,101,IWATER,RETS
    :param time_stamp: For the interval defines the location of the time
        stamp. If set to 'begin', the time stamp is at the begining of the
        interval.  If set to any other string, the reported time stamp will
        represent the end of the interval.  Default is 'begin'.  Place after
        ALL labels.
    '''
    for label in labels:
        ot,lu,sec,vn,lev = label
        nrows = ndata.ix[ot,int(lu),sec,vn,int(lev)]
        # Had to leave off the to_period option - couldn't dump different
        # interval series and didn't benefit printing at all since the to_csv
        # command does not pretty print the period.
        tmpres = pd.DataFrame(nrows['value'],
                 columns=['{0}_{1}_{2}_{3}'.format(ot, lu, vn,
                     lev)])#.to_period(freq=code2freqmap[int(lev)])

        if time_stamp == 'begin':
            tmpres = tmpres.tshift(-1)
        try:
            result = result.join(tmpres)
        except NameError:
            result = tmpres
    return result


@baker.command
def time_series(hbnfilename, interval, *labels, **time_stamp):

    try:
        time_stamp = time_stamp['time_stamp']
    except KeyError:
        time_stamp = 'begin'
    if time_stamp not in ['begin', 'end']:
        raise ValueError('The "time_stamp" optional keyword must be either '
            '"begin" or "end".  You gave {0}'.format(time_stamp))

    if interval.lower() not in ['bivl', 'daily', 'monthly', 'yearly']:
        raise ValueError('The "interval" arguement must be one of "bivl", '
                         '"daily", "monthly", or "yearly".  You supplied '
                         '"{0}"'.format(interval))
    interval = interval.lower()

    ndata = _collect(hbnfilename)
    lablist = ['{0},{1}'.format(i, interval2codemap[interval.lower()]) for i in labels]
    lablist = _process_label_lists(ndata, lablist)
    tsutils.printiso(_collect_time_series(ndata, lablist,
        time_stamp=time_stamp))


def _oldcollect_time_series(ndata, labels, time_stamp='begin'):
    for label in labels:
        try:
            ot,lu,sec,vn,lev = label.split(',')
        except AttributeError:
            ot,lu,sec,vn,lev = label
        print ot,int(lu),sec,vn,int(lev)
        nrows = ndata.ix[ot,int(lu),sec,vn,int(lev)]
        # Had to leave off the to_period option - couldn't dump different
        # interval series and didn't benefit printing at all since the to_csv
        # command does not pretty print the period.
        tmpres = pd.DataFrame(nrows['value'],
                 columns=['{0}_{1}_{2}_{3}'.format(ot, lu, vn,
                     lev)])#.to_period(freq=code2freqmap[int(lev)])

        if time_stamp == 'begin':
            tmpres = tmpres.tshift(-1)

        try:
            result = result.join(tmpres)
        except NameError:
            result = tmpres
    return result


def oldtime_series(hbnfilename, interval, *labels, **time_stamp):
    '''
    Prints out data to the screen from a HSPF binary output file.
    :param hbnfilename: The HSPF binary output file
    :param interval: One of 'yearly', 'monthly', 'daily', or 'BIVL'.
        The 'BIVL' option is a sub-daily interval defined in the UCI file.
        Typically 'BIVL' is used for hourly output, but can be set to any
        value that evenly divides into a day.
    :param labels: The remaining arguments uniquely identify a time-series
        in the binary file.  The format is
        'OPERATIONTYPE,ID,SECTION,VARIABLE'.
        For example: PERLND,101,PWATER,UZS IMPLND,101,IWATER,RETS
    :param time_stamp: For the interval defines the location of the time
        stamp. If set to 'begin', the time stamp is at the begining of the
        interval.  If set to any other string, the reported time stamp will
        represent the end of the interval.  Default is 'begin'.  Place after
        ALL labels.
    '''
    try:
        time_stamp = time_stamp['time_stamp']
    except KeyError:
        time_stamp = 'begin'
    if time_stamp not in ['begin', 'end']:
        raise ValueError('The "time_stamp" optional keyword must be either '
            '"begin" or "end".  You gave {0}'.format(time_stamp))
    ndata = _collect(hbnfilename)
    lablist = ['{0},{1}'.format(i, interval2codemap[interval.lower()]) for i in labels]
    tsutils.printiso(_collect_time_series(ndata, lablist,
        time_stamp=time_stamp))


@baker.command
def dump(hbnfilename):
    ndata = _collect(hbnfilename)
    cdata = zip(ndata.index.get_level_values('opertype'),
                ndata.index.get_level_values('land_use'),
                ndata.index.get_level_values('section'),
                ndata.index.get_level_values('variable_name'))
    cdata = sorted(set(cdata))
    ncdata = []
    for ot,lu,sec,vn in cdata:
        nrows = ndata.ix[ot,int(lu),sec,vn]
        levels = sorted(set(nrows.index.get_level_values('levels')))
        lev = levels[0]
        ncdata.append([ot,lu,sec,vn,lev])
    tsutils.printiso(_collect_time_series(ndata, ncdata))


def main():
    baker.run()
