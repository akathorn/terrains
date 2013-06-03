# -*- coding:utf-8 -*-


def rios(dcel):
    rios = []
    especiales = [ a for a in dcel.edges if arista_especial(a) ]
    for a in especiales:
        v = a.vector
        n = a.face.normalvect
        if v.crossprodZ(n) < 0:
            rios.append(a)
    return rios

def arista_especial(arista):
    if arista.border(): return False
    cara1 = arista.face
    cara2 = arista.twin.face
    vn1 = cara1.normalvect.proyect2D()
    vn2 = cara2.normalvect.proyect2D()
    if vn1.x == 0 and vn1.y == 0: return False
    if vn2.x == 0 and vn2.y == 0: return False
    vector_arista = (arista.destination_vertex.coordinates -\
        arista.origin.coordinates).proyect2D()
    vector_perpendicular = vector_arista.orthogonal2D()
    p1 = vector_arista.crossprodZ(vn1)
    p2 = vector_arista.crossprodZ(vn2)
    return ( (p1 * p2) < 0 or (p1 == 0 and p2 != 0) or (p1 != 0 and p2 == 0) )

def refinar(dcel, lista, mundo_real):
    for v in lista:
        refinar_vertice(dcel, v, mundo_real)
    dcel.delaunay()

def refinar_vertice(dcel, vertice, mundo_real,
                    tolerancia_disminuir = 0.95,
                    tolerancia_aumentar  = -0.2):
    #tolerancia_disminuir > 0
    #tolerancia_aumentar < 0
    if vertice.border():
        return False
    ns = [ f.normalvect for f in vertice.faces ]
    cosines = [ ns[i].cosine(ns[(i+1) % len(ns)])
                for i in xrange(len(ns))]
    if min(cosines) > tolerancia_disminuir:
        dcel.remove_vertex(vertice)
        return True
    elif max(cosines) < tolerancia_aumentar:
        print "Un cosenito pequeñito"
        for i in cercanos(dcel, vertice, mundo_real):
            dcel.add_vertex(i)
            "One point for griffindor"
        return True
    else:
        return False

def cercanos(dcel, vertice, mundo_real):
    caras = dcel.vertices.faces
    res = []
    for v in mundo_real:
        for f in caras:
            if f.inside(v.coordinates):
                res.append(v)
    return res

def rio_arbol(dcel):
    trees = []
    for v in dcel.border_vertices():
        tree = set()
        add = [e for e in v.out_edges if arista_especial(e)]
        while add:
            add_now = list(add)
            for edge in add_now:
                tree.add(edge)
                for other_edge in edge.destination_vertex.out_edges:
                    if arista_especial(other_edge) and (not other_edge in tree):
                        assert arista_especial(other_edge)
                        add_now.append(other_edge)
            add = []
        if tree:
            trees.append(list(tree))

    return trees
