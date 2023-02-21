from rdflib import Graph

from rdf.conftest import TRIPLES
from rdf.utils import graph_from_triples

def canonical_graph():
    return graph_from_triples(TRIPLES)
