from random import random
import numpy
from utils import Vector

def parse(file):
    f = open(file, 'r')

    [ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value] = [_take_number(f.readline())
                                           for i in range(6)]
    rest = f.read().strip().split()

    ncols        = int(ncols)
    nrows        = int(nrows)
    nodata_value = float(nodata_value)

    escala = max(ncols * cellsize, nrows * cellsize) - 1
    points = [ Vector(((i % ncols) * cellsize) / escala,
                      ((i / ncols) * cellsize) / escala,
                      float(rest[i]) / escala)
               for i in xrange(ncols * nrows)
               if float(rest[i]) != nodata_value ]

    return points


def _take_number(cad):
    return float(cad.rstrip().split()[1])
