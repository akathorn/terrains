from random import random
import math

class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y,
                      self.z + other.z)

    def __mul__(self, other):
        # if isinstance(other, Vector):
        #     return self.x * other.x + self.y * other.y + self.z * other.z
        # else:
            return Vector(self.x * other, self.y * other, self.z + other)

    def __sub__(self, other):
        return Vector(self.x - other.x,
                      self.y - other.y,
                      self.z - other.z)

    def __neg__(self):
        return self * -1

    def __div__(self, other):
        return self * (1. / other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __repr__(self):
        return "<" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ">"

    def cosine(self, other):
        return self.dotprod(other)/(self.module3d() * other.module3d())

    def crossprod(self, other):
        return (Vector(self.y*other.z - self.z*other.y,
                      -self.x*other.z + self.z*other.x,
                      self.x*other.y - self.y*other.x))

    def dotprod(self,other):
        return self.dotprod2D(other) + self.z * other.z

    def proyect2D(self):
        return Vector(self.x, self.y, 0)

    def orthogonal2D(self):
        return Vector(-self.y, self.x, 0)

    def crossprodZ(self, other):
        return  self.x*other.y - self.y*other.x

    def dotprod2D(self, other):
        return self.x * other.x + self.y * other.y

    def module(self):
        return (math.sqrt(self.x**2 + self.y**2))

    def module3d(self):
        return (math.sqrt(self.x**2+self.y**2+self.z**2))



def random_filter(lista, prob = 0.5):
    res = []
    for i in lista:
        if random() < prob: res.append(i)
    return res
