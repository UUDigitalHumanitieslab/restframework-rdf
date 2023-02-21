"""
Unittests for the rdfmigrate command.

In the test code, you find multiple expressions of the following form:

    len(left ^ right) == 0

where `left` and `right` are graphs. In short, this expression
evaluates to true if and only if both graphs contain the exact same
set of triples. Please beware that this is not a completely valid way
of comparison when blank nodes are involved!
"""

import pytest

from importlib import import_module
from sys import stdout

from rdflib import Graph

from rdf.utils import graph_from_triples
from rdf.ns import RDF, RDFS
from rdf.migrations import *
from .rdfmigrate import *


@pytest.mark.django_db
def test_migrate_package(app_with_rdf_migrations, app_without_rdf_migrations):
    command = Command()
    command.migrate_package(app_with_rdf_migrations)
    fixture = import_module('.fixture', app_with_rdf_migrations)
    graph = import_module('.graph', app_with_rdf_migrations)
    assert len(graph.graph() ^ fixture.canonical_graph()) == 0
    command.migrate_package(app_without_rdf_migrations)
    # We expect the above line to be a no-op.
    # It must not throw an exception.
    assert True


@pytest.mark.django_db
def test_migrate_graph(empty_graph, filled_graph):
    command = Command()
    backup = graph_from_triples(filled_graph)
    extra = (RDFS.label, RDFS.domain, RDFS.Resource)

    class TestMigration(RDFMigration):
        def actual(self):
            return empty_graph
        def desired(self):
            return filled_graph
        @on_add(RDF.type)
        def insert_extra(self, actual, conjunctive):
            actual.add(extra)

    command.migrate_graph(TestMigration())
    assert len(filled_graph ^ backup) == 0
    assert len(backup - empty_graph) == 0
    assert len(empty_graph - backup) == 1
    assert extra in empty_graph
