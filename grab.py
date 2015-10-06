#!/usr/bin/env python

import sys
import datetime

import numpy
from matplotlib import pyplot
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.dates import epoch2num, date2num


def num_now():
    """
    Return the current date in matplotlib representation
    """
    return date2num(datetime.datetime.now())


def get_limit(past):
    """
    Get the date `past` time ago as the matplotlib representation
    """
    return num_now() - float(past) * 365


def read_dates(limit, stream=sys.stdin):
    """
    Read newline-separated unix time from stream
    """
    dates = []
    for line in stream:
        num = epoch2num(float(line.strip()))
        dates.append(num)
        if num < limit:
            break
    stream.close()
    return dates


def plot_datehist(dates, bins, title=None, logarithmic=False):
    (hist, bin_edges) = numpy.histogram(dates, bins)
    width = bin_edges[1] - bin_edges[0]

    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    ax.bar(bin_edges[:-1], hist / width, width=width)
    ax.set_xlim(bin_edges[0], num_now())
    if logarithmic:
      ax.set_yscale('log')
    ax.set_ylabel('Events [1/day]')
    if title:
        ax.set_title(title)

    # set x-ticks in date
    # see: http://matplotlib.sourceforge.net/examples/api/date_demo.html
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(MonthLocator())
    # format the coords message box
    ax.format_xdata = DateFormatter('%Y-%m-%d')
    ax.grid(True)

    fig.autofmt_xdate()
    return fig


def main():
    from optparse import OptionParser
    parser = OptionParser(usage='PRINT_UNIX_TIME | %prog [options]')
    parser.add_option("-p", "--past", default="3",
                      help="how many years to plot histogram. (default: 3)")
    parser.add_option("-o", "--out", default=None,
                      help="output file. open gui if not specified.")
    parser.add_option("-b", "--bins", default=50, type=int,
                      help="number of bins for histogram. (default: 50)")
    parser.add_option("-t", "--title")
    parser.add_option("-l", "--log", default=False, action="store_true",
                      help="logarithmic scale")
    parser.add_option("-d", "--doc", default=False, action="store_true",
                      help="print document")
    (opts, args) = parser.parse_args()
    print opts

    if opts.doc:
        print __doc__
        return

    dates = read_dates(get_limit(opts.past))
    fig = plot_datehist(dates, opts.bins,
                        title=opts.title, logarithmic=opts.log)

    if opts.out:
        fig.savefig(opts.out)
    else:
        pyplot.show()


if __name__ == '__main__':
    main()
