
class Vertex(object):
    id = 1

    def __init__(self, v = None, e = None):
        self.coordinates = v
        self.out_edge    = e
        self.id = Vertex.id
        Vertex.id += 1


    def __repr__(self):
        rep =  str(self.id)
        rep += ", " + repr(self.coordinates.x)
        rep += ", " + repr(self.coordinates.y)
        rep += ", " + repr(self.coordinates.z)
        rep += ", " + repr(self.out_edge.id)
        return rep


    def __getattr__(self, name):
        if name == "in_edges":
            edges = [self.out_edge.twin]
            n = self.out_edge.twin.next

            while n != self.out_edge:
                edges.append(n.twin)
                n = n.twin.next

            return edges
        elif name == "out_edges":
            edges = [self.out_edge]
            n = self.out_edge.twin.next

            while n != self.out_edge:
                edges.append(n)
                n = n.twin.next

            return edges
        elif name == "edges":
            edges = self.in_edges
            edges.extend(self.out_edges)
            return edges
        elif name == "faces":
            faces = set([e.face for e in self.edges if e.face])
            return list(faces)
        elif name == "polygon":
            return [e.next for e in self.out_edges]
        else:
            raise AttributeError

    def border(self):
        return any([e.border() for e in self.edges])

