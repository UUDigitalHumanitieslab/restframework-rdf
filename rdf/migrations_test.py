from rdflib import URIRef, Graph

from .migrations import *


class TestMigration(RDFMigration):
    def actual(self):
        return Graph()

    def desired(self):
        return Graph()

    @on_add('http://example.com/')
    def process_addition(self, actual, conjunctive):
        pass

    @on_remove('http://other-example.com/')
    def process_deletion(self, actual, conjunctive):
        pass


def test_RDFMigration():
    tester = TestMigration()
    assert len(tester.actual()) == 0
    assert len(tester.desired()) == 0
    assert tester.add_handlers == {
        URIRef('http://example.com/'): 'process_addition',
    }
    assert tester.remove_handlers == {
        URIRef('http://other-example.com/'): 'process_deletion',
    }
