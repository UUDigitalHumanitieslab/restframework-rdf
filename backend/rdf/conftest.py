from importlib import import_module

from pytest import fixture

from rdflib import Graph

from .ns import *

TRIPLES = (
    (RDF.type, RDF.type, RDF.Property),
    (RDF.type, RDFS.range, RDFS.Class),
    (RDFS.range, RDFS.domain, RDF.Property),
    (RDFS.domain, RDFS.domain, RDF.Property),
)


@fixture
def triples():
    return TRIPLES


@fixture
def empty_graph():
    return Graph()


@fixture
def filled_graph(triples):
    g = Graph()
    for t in triples:
        g.add(t)
    return g


@fixture
def app_with_rdf_migrations():
    from .test_apps import with_migrations
    yield with_migrations.__name__
    # Make sure the graph is empty again after use
    graph = import_module('.graph', with_migrations.__name__)
    g = graph.graph
    for t in g:
        g.remove(t)


@fixture
def app_without_rdf_migrations():
    from .test_apps import without_migrations
    return without_migrations.__name__
