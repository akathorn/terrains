# -*- coding:utf-8 -*-

from utils import Vector
from vertex import Vertex
from edge import Edge, enlazar
from face import Face

class DCEL(object):
    def __init__(self):
        object.__init__(self)
        self.vertices = []
        self.faces = []
        self.edges = []

        self.updated = False

        self.initial_vertices = []

    def initial_triangulation(self):
        n1 = Edge(); n2 = Edge(); n3 = Edge(); n4 = Edge()
        p1 = Edge(); p2 = Edge(); p3 = Edge(); p4 = Edge()
        c1 = Edge(); c2 = Edge()

        self.edges = [n1,n2,n3,n4,p1,p2,p3,p4,c1,c2]

        topleft     = Vertex(Vector(-0.1, 1.1, 0), p2)
        topright    = Vertex(Vector(1.1, 1.1, 0), p1)
        bottomleft  = Vertex(Vector(-0.1, -0.1, 0), p3)
        bottomright = Vertex(Vector(1.1, -0.1, 0), p4)
        self.vertices    = [topleft, topright, bottomleft, bottomright]
        self.initial_vertices = [topleft, topright, bottomleft, bottomright]

        a     = Face(p1)
        b     = Face(p2)
        self.faces = [a, b]

        n1.setAttributes(topleft, p1, None, n4, n2)
        n2.setAttributes(bottomleft, p2, None, n1, n3)
        n3.setAttributes(bottomright, p3, None, n2, n4)
        n4.setAttributes(topright, p4, None, n3, n1)

        p1.setAttributes(topright, n1, a, c1, p4)
        p2.setAttributes(topleft, n2, b, p3, c2)
        p3.setAttributes(bottomleft, n3, b, c2, p2)
        p4.setAttributes(bottomright, n4, a, p1, c1)

        c1.setAttributes(topleft,     c2, a, p4, p1)
        c2.setAttributes(bottomright, c1, b, p2, p3)

        self.updated = True

    def remove_initial(self):
        for v in self.initial_vertices:
            self.remove_vertex(v)

        self.initial_vertices = []
#        self.delaunay()

        self.updated = True


    def remove_vertex(self, v):
        # TODO: comprobar si es borde

        # Hacer convexo el resto
        repetir = True;
        while repetir:
            repetir = False;
            for edge in v.edges:
                if edge.border():
                    pass
                elif not edge.convex():
                    # Esta mal, la flipamos
                    edge.flip()
                    repetir = True
                    break

        if len(v.out_edges) == 4:
            v.out_edges[0].flip()


        # Borrar las aristas
        for edge in v.edges:
            self.edges.remove(edge)

        # Borrar las caras
        for face in v.faces:
            self.faces.remove(face)

        # Borrar el vértice
        self.vertices.remove(v)

        if v.border():
            new_face = None
        else:  #Creamos la nueva cara (en el borde era None)
            new_face = Face(v.out_edge.next)
            self.faces.append(new_face)

        # Arreglar referencias
        for edge in v.out_edges:
            e1 = edge.next
            e2 = edge.twin.prev
            a  = edge.twin.origin
            e1.face = new_face
            e2.face = new_face
            a.out_edge = e1
            e1.prev = e2
            e2.next = e1

        if new_face:
            self.delaunay_rec(new_face.edges)

        self.updated = True


    def add_points(self, points):
        last_face = None

        for point in points:
            face = self.find_face(point, suggested_face = last_face)
            [vertex, edges, faces] = self.split_face(face, point)
            last_face = faces[0]
            self.delaunay_rec(vertex.polygon)

        self.updated = True



    def add_point(self, point):
        #TODO: Caso de caer en una arista
        face = self.find_face(point)
        self.split_face(face, point)

        self.updated = True

    def find_face(self, point, suggested_face = None):
        if suggested_face:
            current_face = suggested_face
        else:
            current_face = self.faces[0]

        found = False
        while (not found) and current_face:
            vs = [Vector(v.coordinates.x,
                     v.coordinates.y,
                     0)
                  for v in current_face.vertices]
            cps = [(vs[i] - point).crossprodZ(vs[(i+1) %3] - point)
                   for i in range(3)]
            if cps[0] < 0:
                adyacent   = current_face.edges[0]
                current_face = adyacent.twin.face
            elif cps[1] < 0:
                adyacent = current_face.edges[1]
                current_face = adyacent.twin.face
            elif cps[2] < 0:
                adyacent = current_face.edges[2]
                current_face = adyacent.twin.face
            else:
                found = True

        return current_face


    def split_face(self, face, point):
        self.faces.remove(face)
        [e1, e2, e3] = face.edges
        [a, b, c]    = face.vertices
        a1 = Edge(); a2 = Edge()
        b1 = Edge(); b2 = Edge()
        c1 = Edge(); c2 = Edge()

        v = Vertex(point, a2)

        f1 = Face(a2)
        f2 = Face(b2)
        f3 = Face(c2)

        e1.next = b1; e1.prev = a2; e1.face = f1
        e2.next = c1; e2.prev = b2; e2.face = f2
        e3.next = a1; e3.prev = c2; e3.face = f3

        # setAttributes(origin, twin, face, next, prev):
        a1.setAttributes (a, a2, f3, c2, e3)
        a2.setAttributes (v, a1, f1, e1, b1)
        b1.setAttributes (b, b2, f1, a2, e1)
        b2.setAttributes (v, b1, f2, e2, c1)
        c1.setAttributes (c, c2, f2, b2, e2)
        c2.setAttributes (v, c1, f3, e3, a1)

        self.vertices.append(v)
        self.edges.extend([a1,a2,b1,b2,c1,c2])
        self.faces.extend([f1,f2,f3])

        return [v,[a1,a2,b1,b2,c1,c2],[f1,f2,f3]]

        self.updated = True

    def delaunay(self):
        repeat = True
        while repeat:
            repeat = False

            for e in self.edges:
                if e.legalize():
                    repeat = True

        self.updated = True

    def delaunay_rec(self, edges):
        while edges:
            pendientes = []
            for e in edges:
                if e.legalize():
                    for a in e.polygon_edges:
                        pendientes.append(a)
            edges = pendientes

        self.updated = True


    def border_vertices(self):
        return [v for v in self.vertices if v.border()]
