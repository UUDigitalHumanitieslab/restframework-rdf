from rdflib import Graph

from rdf.conftest import TRIPLES

def canonical_graph():
    g = Graph()
    for t in TRIPLES:
        g.add(t)
    return g
