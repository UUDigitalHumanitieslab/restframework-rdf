from importlib import import_module
from datetime import datetime, date

from django.conf import settings
from pytest import fixture
from rdf.utils import graph_from_triples, prune_triples
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import ConjunctiveGraph, Graph, Literal, URIRef

from .ns import *

CREATION_DATE = Literal(datetime.now())

ITEM = Namespace('http://localhost:8000/item/')
STAFF = Namespace('http://localhost:8000/staff#')
ONTO = Namespace('http://localhost:8000/ontology#')
SOURCE = Namespace('http://localhost:8000/source/')

ITEMS = (
    ( ITEM['1'], RDF.type,              OA.TextQuoteSelector               ),
    ( ITEM['1'], OA.prefix,             Literal('this is the start of ')   ),
    ( ITEM['1'], OA.exact,              Literal('the exact selection')     ),
    ( ITEM['1'], OA.suffix,             Literal(' and this is the end')    ),
    ( ITEM['1'], DCTERMS.creator,       STAFF.tester                       ),
    ( ITEM['1'], DCTERMS.created,       CREATION_DATE                      ),

    # Items 2 and 3 dropped out for historical reasons.

    ( ITEM['4'], RDF.type,              OA.TextPositionSelector            ),
    ( ITEM['4'], OA.start,              Literal(22)                        ),
    ( ITEM['4'], OA.end,                Literal(41)                        ),
    ( ITEM['4'], DCTERMS.creator,       STAFF.tester                       ),
    ( ITEM['4'], DCTERMS.created,       CREATION_DATE                      ),

    ( ITEM['5'], RDF.type,              OA.SpecificResource                ),
    ( ITEM['5'], OA.hasSource,          SOURCE['1']                        ),
    ( ITEM['5'], OA.hasSelector,        ITEM['4']                          ),
    ( ITEM['5'], OA.hasSelector,        ITEM['1']                          ),
    ( ITEM['5'], DCTERMS.creator,       STAFF.tester                       ),
    ( ITEM['5'], DCTERMS.created,       CREATION_DATE                      ),

    ( ITEM['6'], RDF.type,              ONTO.reader                        ),
    ( ITEM['6'], SKOS.prefLabel,        Literal('Margaret Blessington')    ),
    ( ITEM['6'], ONTO.is_identified_by, Literal('Margaret Gardiner Blessington') ),
    ( ITEM['6'], ONTO.is_identified_by, Literal('Marguerite Gardiner, countess of Blessington') ),
    ( ITEM['6'], ONTO.has_gender,       Literal('female')                  ),
    ( ITEM['6'], ONTO.has_occupation,   Literal('novelist')                ),
    ( ITEM['6'], ONTO.has_occupation,   Literal('writer')                  ),
    ( ITEM['6'], ONTO.has_nationality,  Literal('Irish')                   ),
    ( ITEM['6'], CIDOC.was_born,        Literal(date(1789, 9, 1))          ),
    ( ITEM['6'], CIDOC.died,            Literal(date(1849, 6, 4))          ),
    ( ITEM['6'], OWL.sameAs,            URIRef('https://en.wikipedia.org/wiki/Marguerite_Gardiner,_Countess_of_Blessington') ),
    ( ITEM['6'], DCTERMS.type,          Literal('example data')            ),
    ( ITEM['6'], DCTERMS.creator,       STAFF.tester                       ),
    ( ITEM['6'], DCTERMS.created,       CREATION_DATE                      ),

    ( ITEM['7'], RDF.type,              OA.Annotation                      ),
    ( ITEM['7'], OA.hasBody,            ONTO.reader                        ),
    ( ITEM['7'], OA.hasBody,            ITEM['6']                          ),
    ( ITEM['7'], OA.hasTarget,          ITEM['5']                          ),
    ( ITEM['7'], OA.motivatedBy,        OA.tagging                         ),
    ( ITEM['7'], OA.motivatedBy,        OA.identifying                     ),
    ( ITEM['7'], DCTERMS.creator,       STAFF.tester                       ),
    ( ITEM['7'], DCTERMS.created,       CREATION_DATE                      ),
)


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
def items():
    return ITEMS


@fixture
def filled_graph(triples):
    return graph_from_triples(triples)


@fixture
def filled_conjunctive_graph(items):
    return graph_from_triples(items, ConjunctiveGraph)


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


@fixture
def prefixed_query():
    return '''
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://www.schema.org/>
    SELECT ?s ?p ?o WHERE { ?s ?p ?o }
    '''


HAS_TRIPLES = '''
ASK {
    GRAPH ?g {
        ?s ?p ?o
    }
}
'''

@fixture
def sparqlstore(settings):
    store = settings.RDFLIB_STORE
    store.update('CLEAR ALL')
    assert not store.query(HAS_TRIPLES)
    yield store
    store.update('CLEAR ALL')

