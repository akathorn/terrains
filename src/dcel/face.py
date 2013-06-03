import math

from utils import Vector

class Face(object):
    id = 1

    def __init__(self, e = None):
        self.edge = e

        self.id = Face.id
        Face.id += 1

    def __repr__(self):
        return str(self.id) + ", " + repr(self.edge.id)


    def __getattr__(self, name):
        if name == "vertices":
            vs = [self.edge.origin,
                  self.edge.next.origin,
                  self.edge.next.next.origin]
            return vs
        elif name == "edges":
            es = [self.edge,
                  self.edge.next,
                  self.edge.next.next]
            return es
        elif name == "normalvect":
            v1 = (self.edge.next.origin.coordinates - self.edge.origin.coordinates)
            v2 = (self.edge.prev.origin.coordinates - self.edge.origin.coordinates)
            norm = v1.crossprod(v2)
            if norm.z >= 0:
                return norm
            return norm*(-1)
        else:
            raise AttributeError

    def inside(self, point):
        vs = [Vector(v.coordinates.x,
                     v.coordinates.y,
                     0)
              for v in self.vertices]
        cps = [(vs[i] - point).crossprodZ(vs[(i+1) %3] - point) >=0
                        for i in range(3)]

        return all(cps)


    def angles(self):
        cosines = []

        vs = [v.coordinates for v in self.vertices]

        truncar = lambda x: math.trunc(x * 1e15) / 1e15

        for i in range(0,3):
            a = vs[i]
            b = vs[(i+1) % 3]
            c = vs[(i-1) % 3]
            v1 = b - a
            v2 = c - a
            cosines.append(
                truncar(v1.dotprod2D(v2) /(v1.module() * v2.module()))
                )

        return map(math.acos, cosines)
