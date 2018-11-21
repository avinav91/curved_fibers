#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data_proc.py
Obtaining coordinates for fiber paths and calculating fiber boundaries and plotting
- Reads csv data of fiber paths
-calculates mid angle in x-direction for FEA calculations
-plot fiber paths

"""


from __future__ import print_function
#from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from argparse import ArgumentParser
import numpy as np
import matplotlib.pyplot as plt
import os



SUCCESS = 0
INVALID_DATA = 1
IO_ERROR = 2

DEFAULT_DATA_FILE_NAME = 'data\Ply_1_Left.csv'


def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)


def data_analysis(data_array,angle):
    """
    Finds the co-ordinates to place middle matrix region for future FEA modeling, calculates angle at the middle

    Parameters
    ----------
    data_array : numpy array of y co-ordinates (col-1) and x co-ordinates (col-2) of left boundary of a fiber
    placement machine run

    Returns
    -------
    data_xLMid : numpy array with middle matrix co-ordinates

    Optional : If flag -a then calculates and prints mid angle values
    """
    num_points, num_fibers = data_array.shape
    data_xLMid=np.zeros((num_points-1,num_fibers))
    data_midAngle=np.zeros((num_points-1,num_fibers-1))
    for i in range(num_fibers):
        for j in range(1, num_points):
            data_xLMid[j-1][i]=(data_array[j][i]+data_array[j-1][i])*0.5

    if angle:
        for i in range(num_fibers):
            for j in range(1, num_points):
                if i>=1:
                    data_midAngle[j-1][i-1]=np.arctan((data_array[j][1]-data_array[j-1][1])/(data_array[j][i]-data_array[j-1][i]))
        np.savetxt('data_mid_angle.csv', data_midAngle, delimiter=',')
        print("Wrote file: {}".format('data_mid_angle.csv'))



    return data_xLMid


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = ArgumentParser(description='Reads in a csv (no header) of x,y coordinates and gets the mean of x for  '
                                        'middle matrix region. There must be the same number of values in each row.')
    parser.add_argument("-c", "--csv_data_file", help="The location (directory and file name) of the csv file with "
                                                      "data to analyze",
                        default=DEFAULT_DATA_FILE_NAME)
    parser.add_argument("-a", "--angle", help="Calculate the fiber angle at the midpoints of "
                                                         "Each fiber path boundaries", action="store_true", default= False)
    args = None
    try:
        args = parser.parse_args(argv)
        args.csv_data = np.loadtxt(fname=args.csv_data_file, delimiter=',')
    except IOError as e:
        warning("Problems reading file:", e)
        parser.print_help()
        return args, IO_ERROR
    except ValueError as e:
        warning("Read invalid data:", e)
        parser.print_help()
        return args, INVALID_DATA

    return args, SUCCESS


def plot_stats(f_name,data_xLMid):
    """
    Makes a plot of middle matrix paths
    :param data_xLMid: numpy array middle matrix co-ordinates
    :param f_name: File name to save to
    :return: saves a png file
    """
    num_midpoints, num_fibers = data_xLMid.shape
    plt.figure()
    plt.xlim(-10.0,10.0)
    plt.ylim(-10.0,10.0)
    for i in range(num_fibers-1):
        # red dashes, blue squares and green triangles
        plt.plot(data_xLMid[:,i+1], data_xLMid[:,0])

    plt.title('Sample path of matrix around fiber paths')
    plt.xlabel('X co-ordinate values')
    plt.ylabel('Y co-ordinate values')
    out_name = f_name + ".png"
    plt.savefig(out_name)
    print("Wrote file: {}".format(out_name))


def main(argv=None):
    args, ret = parse_cmdline(argv)
    if ret != SUCCESS:
        return ret
    data_xLMid = data_analysis(args.csv_data, args.angle)

    '''
    This section is to identify the input file name and create the output file name
    '''
    # get the name of the input file without the directory it is in, if one was specified
    base_out_fname = os.path.basename(args.csv_data_file)
    # get the first part of the file name (omit extension) and add the suffix
    base_out_fname = os.path.splitext(base_out_fname)[0] + '_MidMtrx'
    # add suffix and extension
    out_fname = base_out_fname + '.csv'

    ''' 
    Saves the data to the file name obtained
    '''
    np.savetxt(out_fname, data_xLMid, delimiter=',')
    print("Wrote file: {}".format(out_fname))

    # send the base_out_fname and data to a new function that will plot the data
    plot_stats(base_out_fname, data_xLMid)
    return SUCCESS  # success


if __name__ == "__main__":
    status = main()
    sys.exit(status)
