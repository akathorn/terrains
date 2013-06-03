# -*- coding:utf-8 -*-

from utils import Vector

class Edge(object):
    id = 1

    def __init__(self, origin = None, twin = None,
                 face = None, n = None, p = None):
        self.setAttributes(origin, twin, face, n, p)
        self.id = Edge.id
        Edge.id += 1

    def setAttributes(self, origin, twin, face, n, p):
        self.origin = origin
        self.twin = twin
        self.face = face
        self.next = n
        self.prev = p

    def __repr__(self):
        rep = str(self.id)
        rep += ", " + repr(self.origin.id)
        rep += ", " + repr(self.twin.id)
        if self.face:
            rep += ", " + repr(self.face.id)
        else:
            rep += ", 0"
        rep += ", " + repr(self.next.id)
        rep += ", " + repr(self.prev.id)
        return rep


    def __getattr__(self, name):
        if name == "vertices":
            vs = [self.origin,
                  self.twin.origin]
            return vs
        elif name == "destination_vertex":
            return self.twin.origin
        elif name == "opposite_vertex":
            return self.prev.origin
        elif name == "vector":
            return self.destination_vertex.coordinates -\
                self.origin.coordinates
        elif name == "polygon_edges":
            return [self.next,self.prev,self.twin.next,self.twin.prev]
        else:
            raise AttributeError

    def inside(self, point):
        [v1,v2] = [v.coordinates for v in self.vertices]
        return (v1 - point).crossprodZ(v2 - point) == 0

    def border(self):
        return (not self.face) or (not self.twin.face)

    def flip(self):
        if self.border():
            return False

        a1 = self
        a2 = a1.twin

        e1 = a1.next
        e2 = a1.prev

        e3 = a2.next
        e4 = a2.prev

        v1 = a1.origin
        v2 = e4.origin
        v3 = a2.origin
        v4 = e2.origin

        A = a1.face
        B = a2.face
        A.edge = a1
        B.edge = a2

        # setAttributes(origin, twin, face, next, prev):
        a1.setAttributes (v2, a2, A, e2, e3)
        a2.setAttributes (v4, a1, B, e4, e1)

        v1.out_edge = e3
        v3.out_edge = e1

        e1.face = B
        e3.face = A

        enlazar(a1,e2,e3)
        enlazar(a2,e4,e1)

        return True


    def convex(self):
        # Concavidad
        a = self.origin.coordinates
        b = self.twin.origin.coordinates
        c = self.opposite_vertex.coordinates
        d = self.twin.opposite_vertex.coordinates

        return (d - a).crossprodZ(c - a) * (c - b).crossprodZ(d - b) <= 0

    def legalize(self):
        if self.border():
            pass #print "Borde"
            return False

        if self.convex():
            return False

        # Vale, no es cóncavo...
        min_angle = \
                  min(min(self.face.angles()),min(self.twin.face.angles()))
        self.flip()
        new_min_angle = \
                  min(min(self.face.angles()),min(self.twin.face.angles()))

        pass#print self.face.angles(), self.twin.face.angles()
        if new_min_angle <= min_angle:
            self.flip()
            pass#print "No mejora"
            return False
        else:
            pass#print "Flipada"
            return True


def enlazar(a,b,c):
    a.next = b; b.next = c; c.next = a
    c.prev = b; b.prev = a; a.prev = c;

