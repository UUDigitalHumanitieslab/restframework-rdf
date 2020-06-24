from types import SimpleNamespace

import pytest
from rdflib import Literal

from rdf.ns import RDF, SCHEMA
from rdf.utils import graph_from_triples

from nlp_ontology import namespace as my
from nlp_ontology.graph import graph

TRIPLES = (
    (my.icecream,   RDF.type,       SCHEMA.Food),
    (my.icecream,   SCHEMA.color,   Literal("#f9e5bc")),
    (SCHEMA.Cat,    my.meow,        Literal('loud')),
)

INSERT_QUERY = '''
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX my: <http://testserver/nlp-ontology#>
    PREFIX dctypes: <http://purl.org/dc/dcmitype/>
    PREFIX ns3: <http://schema.org/>

    INSERT DATA { 
        my:icecream         a               ns3:Food        ;
                            ns3:color       "#f9e5bc"       .
        ns3:Cat             my:meow         "loud"          .
    }
'''

SELECT_QUERY = '''
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
'''

ASK_QUERY = '''PREFIX my: <http://testserver/nlp-ontology#> 
ASK { ?x my:meow  "loud" }'''
ASK_QUERY_FALSE = '''PREFIX my: <http://testserver/nlp-ontology#> 
ASK { ?x my:meow  "silent" }'''

CONSTRUCT_QUERY = '''
    PREFIX my: <http://testserver/nlp-ontology#>
    PREFIX ns3: <http://schema.org/>
    CONSTRUCT WHERE { ?x my:meow ?name } 
'''


@pytest.fixture
def ontologygraph():
    g = graph_from_triples(TRIPLES)
    return g


@pytest.fixture
def ontologygraph_db(db, ontologygraph):
    g = graph()
    g += ontologygraph
    yield
    g -= ontologygraph


@pytest.fixture
def test_queries():
    values = {
        'ASK_TRUE': ASK_QUERY,
        'ASK_FALSE': ASK_QUERY_FALSE,
        'CONSTRUCT': CONSTRUCT_QUERY,
        'SELECT': SELECT_QUERY,
        'INSERT': INSERT_QUERY
    }
    return SimpleNamespace(**values)


@pytest.fixture
def accept_headers():
    values = {
        'turtle': 'text/turtle',
        'sparql_json': 'application/sparql-results+json',
        'json': 'application/json'
    }
    return SimpleNamespace(**values)
