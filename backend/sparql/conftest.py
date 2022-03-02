from types import SimpleNamespace

import pytest
from django.contrib.auth.models import Permission, User
from rdflib import Literal

from nlp_ontology import namespace as my
from sources.graph import graph
from rdf.ns import RDF, SCHEMA
from rdf.utils import graph_from_triples
from sources.constants import SOURCES_NS
from nlp_ontology.constants import NLP_ONTOLOGY_NS

INSERT_QUERY = '''
    PREFIX my: <http://testserver/nlp-ontology#>
    PREFIX ns3: <http://schema.org/>

    INSERT DATA {
        my:icecream         a               ns3:Food        ;
                            ns3:color       "#f9e5bc"       .
        ns3:Cat             my:meow         "loud"          .
    }
'''

DELETE_DATA_QUERY = '''
    PREFIX my: <http://testserver/nlp-ontology#>
    PREFIX ns3: <http://schema.org/>

    DELETE DATA {
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

SELECT_FROM_NLP_QUERY = '''
    SELECT ?s ?p ?o
    FROM <{ns}>
    WHERE {{
        ?s ?p ?o .
    }}
'''.format(ns=NLP_ONTOLOGY_NS)

SELECT_FROM_SOURCES_QUERY = '''
    SELECT ?s ?p ?o
    FROM <{ns}>
    WHERE {{
        ?s ?p ?o .
    }}
'''.format(ns=SOURCES_NS)

ASK_QUERY = '''PREFIX my: <http://testserver/nlp-ontology#>
ASK { ?x my:meow  "loud" }'''
ASK_QUERY_FALSE = '''PREFIX my: <http://testserver/nlp-ontology#>
ASK { ?x my:meow  "silent" }'''

CONSTRUCT_QUERY = '''
    PREFIX my: <http://testserver/nlp-ontology#>
    PREFIX ns3: <http://schema.org/>
    CONSTRUCT WHERE { ?x my:meow ?name }
'''

DELETE_QUERY = '''
    PREFIX my: <{ns}>
    DELETE {{ ?s ?p ?o }} WHERE {{ ?s ?p ?o ; my:meow "loud" }}
'''.format(ns=NLP_ONTOLOGY_NS)

DELETE_FROM_QUERY = '''
    PREFIX my: <{ns}>
    DELETE {{ GRAPH <{graph}> {{ ?s ?p ?o }} }} WHERE {{ ?s ?p ?o ; my:meow "loud" }}
'''.format(ns=NLP_ONTOLOGY_NS, graph=NLP_ONTOLOGY_NS)


@pytest.fixture
def triples():
    return (
        (my.icecream,   RDF.type,       SCHEMA.Food),
        (my.icecream,   SCHEMA.color,   Literal("#f9e5bc")),
        (SCHEMA.Cat,    my.meow,        Literal('loud')),
    )


@pytest.fixture
def ontologygraph(triples):
    g = graph_from_triples(triples)
    return g


@pytest.fixture
def graph_db(db, sparqlstore):
    return graph()


@pytest.fixture
def ontologygraph_db(db, ontologygraph, sparqlstore):
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
        'SELECT_FROM_NLP': SELECT_FROM_NLP_QUERY,
        'SELECT_FROM_SOURCES': SELECT_FROM_SOURCES_QUERY,
        'INSERT': INSERT_QUERY,
        'DELETE': DELETE_QUERY,
        'DELETE_DATA': DELETE_DATA_QUERY,
        'DELETE_FROM': DELETE_FROM_QUERY
    }
    return SimpleNamespace(**values)


@ pytest.fixture
def accept_headers():
    values = {
        'turtle': 'text/turtle',
        'sparql_json': 'application/sparql-results+json',
        'sparql_xml': 'application/sparql-results+xml',
        'sparql_csv': 'text/csv',
        'json': 'application/json',
        'rdfxml': 'application/rdf+xml',
        'ntriples': 'application/n-triples',
        'jsonld': 'application/ld+json'
    }
    return SimpleNamespace(**values)


@pytest.fixture
def sparql_user(db):
    user = User.objects.create_user(username='john', password='')
    update_perm = Permission.objects.get(codename='sparql_update')
    user.user_permissions.add(update_perm)
    return user


@pytest.fixture
def sparql_client(client, sparql_user):
    client.login(username=sparql_user.username, password='')
    return client


@pytest.fixture
def unsupported_queries():
    queries = {
        'LOAD': 'LOAD <{}> INTO GRAPH <{}>'.format(SOURCES_NS, NLP_ONTOLOGY_NS),
        'CLEAR_ALL': 'CLEAR ALL',
        'CLEAR': 'CLEAR GRAPH <{}>'.format(NLP_ONTOLOGY_NS),
        'DROP': 'CLEAR GRAPH <{}>'.format(NLP_ONTOLOGY_NS),
        'ADD': 'ADD <{}> TO <{}>'.format(SOURCES_NS, NLP_ONTOLOGY_NS),
        'MOVE': 'MOVE <{}> TO <{}>'.format(SOURCES_NS, NLP_ONTOLOGY_NS),
        'COPY': 'COPY <{}> TO <{}>'.format(SOURCES_NS, NLP_ONTOLOGY_NS),
        'CREATE': 'CREATE GRAPH <http://testserver/newgraph#>'
    }

    return queries


@pytest.fixture
def blanknode_queries():
    triples = (
        ('[ :p "v" ]'),
        ('[] :p "v"'),
        ('_:b57 :p "v"'),
    )
    return ['INSERT DATA {{ {} }}'.format(t) for t in triples]
