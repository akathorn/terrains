from dcel import Edge, Face, Vertex
from utils import Vector

def save(dcel, filename):
    f = open(filename, "w")

    print >> f, "VERTICES "
    for vertex in dcel.vertices:
        print >> f, vertex

    print >> f, "FACES "
    for face in dcel.faces:
        print >> f, face

    print >> f, "EDGES "
    for edge in dcel.edges:
        print >> f, edge

    f.close()

def load(dcel, filename):
    f = open(filename, "r")
    lines = [line.strip() for line in f.readlines()]
    f.close()

    vertices = {}
    edges    = {}
    faces    = {}

    section_vertices = lines.index("VERTICES")
    section_faces    = lines.index("FACES")
    section_edges    = lines.index("EDGES")

    for line in lines[section_vertices + 1 : section_faces]:
        fields = [ field.strip() for field in line.split(",") ]

        vector = Vector(float(fields[1]),
                        float(fields[2]),
                        float(fields[3]))

        vertex = Vertex(vector)

        vertex.id = int(fields[0])

        vertices[int(fields[0])] = (vertex, fields[4])

    for line in lines[section_faces + 1 : section_edges]:
        fields = [ field.strip() for field in line.split(",") ]

        face = Face()
        face.id = int(fields[0])

        faces[int(fields[0])] = (face, fields[1])

    for line in lines[section_edges + 1:]:
        fields = [ field.strip() for field in line.split(",") ]

        edge = Edge()
        edge.id = int(fields[0])

        edges[int(fields[0])] = (edge, fields[1:])


    for vertex_id in vertices:
        edge_id = int(vertices[vertex_id][1])
        vertices[vertex_id][0].out_edge = edges[edge_id][0]

    for face_id in faces:
        edge_id = int(faces[face_id][1])
        faces[face_id][0].edge = edges[edge_id][0]

    for edge_id in edges:
        fields = map(int, edges[edge_id][1])

        if fields[2] == 0: # No hay cara
            face = None
        else:
            face = faces[fields[2]][0]

        edges[edge_id][0].setAttributes( vertices[fields[0]][0],
                                         edges[fields[1]][0],
                                         face,
                                         edges[fields[3]][0],
                                         edges[fields[4]][0] )

    dcel.vertices = [v[0] for v in vertices.values()]
    dcel.faces    = [f[0] for f in faces.values()]
    dcel.edges    = [e[0] for e in edges.values()]
    dcel.updated  = True
