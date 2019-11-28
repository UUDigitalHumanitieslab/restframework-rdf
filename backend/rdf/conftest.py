from importlib import import_module

from pytest import fixture

from rdflib import Graph, Literal, URIRef

from rdf.utils import graph_from_triples, prune_triples
from .ns import *

MAGIC_NODE = URIRef('http://hogwarts.edu/')

TRIPLES = (
    (RDF.type, RDF.type, RDF.Property),
    (RDF.type, RDFS.range, RDFS.Class),
    (RDF.type, RDFS.label, Literal('type')),
    (RDFS.range, RDFS.domain, RDF.Property),
    (RDFS.domain, RDFS.domain, RDF.Property),
    # following triples added for testing traversal
    # note that these form a ring together with the triples above!
    (RDF.Property, RDF.type, RDFS.Class),
    (RDF.Property, RDFS.subClassOf, RDFS.Resource),
    (RDFS.Resource, RDFS.isDefinedBy, MAGIC_NODE),
    (MAGIC_NODE, RDF.type, RDF.Statement),
    (MAGIC_NODE, RDF.object, RDF.type),
)


@fixture
def triples():
    return TRIPLES


@fixture
def empty_graph():
    return Graph()


@fixture
def filled_graph(triples):
    return graph_from_triples(triples)


@fixture
def app_with_rdf_migrations():
    from .test_apps import with_migrations
    yield with_migrations.__name__
    # Make sure the graph is empty again after use
    graph = import_module('.graph', with_migrations.__name__)
    g = graph.graph()
    prune_triples(g, g)
    assert len(g) == 0


@fixture
def app_without_rdf_migrations():
    from .test_apps import without_migrations
    return without_migrations.__name__
