import pytest

from rdflib import Graph

from .ns import *
from .utils import *


@pytest.fixture
def other_triples():
    return (
        (RDF.type, RDF.type, RDF.Property),
        (RDF.type, RDFS.range, RDFS.Class),
        (RDF.type, RDFS.label, Literal('typo')),  # sic
    )


def test_prune_triples(filled_graph, other_triples):
    before = len(filled_graph)
    prune_triples(filled_graph, other_triples)
    after = len(filled_graph)
    assert before - after == 2


def test_prune_zero(filled_graph):
    prune_triples(filled_graph, filled_graph)
    assert len(filled_graph) == 0


def test_append_triples(filled_graph, other_triples):
    before = len(filled_graph)
    append_triples(filled_graph, other_triples)
    after = len(filled_graph)
    assert after - before == 1


def test_append_identity(filled_graph):
    before = len(filled_graph)
    append_triples(filled_graph, filled_graph)
    after = len(filled_graph)
    assert before == after


def test_graph_from_triples(other_triples):
    result = graph_from_triples(other_triples)
    assert isinstance(result, Graph)
    for t in other_triples:
        assert t in result


def test_traverse_forward(filled_graph, other_triples):
    start = graph_from_triples(other_triples)
    result = traverse_forward(filled_graph, start, 0)
    assert isinstance(result, Graph)
    size = len(result)
    assert size == 0
    for depth in range(1, 4):
        result = traverse_forward(filled_graph, start, depth)
        new_size = len(result)
        assert new_size > size
        size = new_size


def test_traverse_backward(filled_graph, other_triples):
    start = graph_from_triples(other_triples)
    result = traverse_backward(filled_graph, start, 0)
    assert isinstance(result, Graph)
    size = len(result)
    assert size == 0
    for depth in range(1, 4):
        result = traverse_backward(filled_graph, start, depth)
        new_size = len(result)
        assert new_size > size
        size = new_size
