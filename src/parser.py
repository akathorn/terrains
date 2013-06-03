from random import random
from utils import random_filter
import numpy
from DCEL import Point3D

def parse(file):
    f = open(file, 'r')

    [ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value] = [_take_number(f.readline())
                                           for i in range(6)]
    rest = f.read().strip().split()
    points = [Point3D([i % ncols, i / ncols, rest[i]]) for i in xrange(ncols * nrows)]

    utils.random_filter(points)

    print points



def _take_number(cad):
    return int(cad.rstrip().split()[1])
