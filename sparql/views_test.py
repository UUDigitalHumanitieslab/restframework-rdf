import json

import pytest
from rdf.ns import SCHEMA
from rdflib.namespace import Namespace
from rdf.utils import graph_from_triples
from rdflib import XSD, Graph, Literal

from .exceptions import BlankNodeError
from .views import SPARQLUpdateAPIView
from .test_app.views import QueryView, UpdateView
from .conftest import nlp

from rest_framework.test import APIRequestFactory

QUERY_URL = '/test/query'
UPDATE_URL = '/test/update'

@pytest.fixture
def request_factory():
    return APIRequestFactory()

def check_content_type(response, content_type):
    return content_type in response.headers['content-type']


def test_insert(sparql_client, ontologygraph, test_queries, graph_db):
    assert len(graph_db) == 0

    post_response = sparql_client.post(
        UPDATE_URL, {'update': test_queries.INSERT})
    assert post_response.status_code == 200

    get_response = sparql_client.get(QUERY_URL)
    assert get_response.status_code == 200
    assert check_content_type(get_response, 'text/turtle')

    get_data = Graph().parse(data=get_response.content, format='text/turtle')
    assert len(graph_db) != 0
    assert len(get_data ^ ontologygraph) == 0

    # clean up
    sparql_client.post(
        UPDATE_URL, {'update': test_queries.DELETE_DATA})
    assert len(graph_db) == 0

def test_ask(request_factory, test_queries, ontologygraph_db):
    view = QueryView.as_view()
    true_request = request_factory.get(QUERY_URL, {'query': test_queries.ASK_TRUE})
    true_response = view(true_request).render()
    assert true_response.status_code == 200
    assert json.loads(true_response.content.decode('utf8'))['boolean']
    assert check_content_type(true_response, 'application/sparql-results+json')

    false_request = request_factory.get(
        QUERY_URL, {'query': test_queries.ASK_FALSE})
    false_response = view(false_request).render()
    assert false_response.status_code == 200
    assert not json.loads(false_response.content.decode('utf8'))['boolean']


def test_construct(client, test_queries, ontologygraph_db):
    response = client.get(QUERY_URL, {'query': test_queries.CONSTRUCT})
    assert response.status_code == 200

    result_graph = Graph().parse(data=response.content, format='turtle')
    exp_graph = graph_from_triples(
        ((SCHEMA.Cat,    nlp.meow,        Literal("loud", datatype=XSD.string)),)
    )
    assert len(exp_graph ^ result_graph) == 0


def test_malformed(sparql_client, sparqlstore):
    malformed_get = sparql_client.post(
        QUERY_URL, {'query': 'this is no SPARQL query!'})
    assert malformed_get.status_code == 400

    malformed_update = sparql_client.post(
        UPDATE_URL, {'update': 'this is no SPARQL query!'})
    assert malformed_update.status_code == 400


def test_permissions(client, sparql_user, test_queries, sparqlstore):
    res = client.post(UPDATE_URL, {'update': test_queries.INSERT})
    assert res.status_code == 403

    client.login(username=sparql_user.username, password='')
    res = client.post(
        UPDATE_URL, {'update': test_queries.INSERT})
    assert res.status_code == 200


def test_unsupported(sparql_client, unsupported_queries, sparqlstore):
    for query in unsupported_queries.values():
        request = sparql_client.post(UPDATE_URL, {'update': query})
        assert b'Update operation is not supported.' in request.content
        assert request.status_code == 400


def test_delete(sparql_client, test_queries, ontologygraph_db, graph_db):
    # Should not delete if from another endpoint
    delete = sparql_client.post(
        '/sparql/source/update', {'update': test_queries.DELETE_FROM})
    assert delete.status_code == 400
    res = sparql_client.get(QUERY_URL).content
    assert len(Graph().parse(data=res, format='turtle')) == 3

    # Should delete if endpoint and graph match
    assert len(graph_db) != 2
    delete = sparql_client.post(
        UPDATE_URL, {'update': test_queries.DELETE})
    assert delete.status_code == 200
    res = sparql_client.get(QUERY_URL).content
    assert len(Graph().parse(data=res, format='turtle')) == 2
    assert len(graph_db) == 2


def test_select_from(sparql_client, test_queries, ontologygraph_db, ontologygraph, accept_headers):
    # Should not return results if querying a different endpoint
    # Note that any triples in VOCAB_NS graph would be returned here
    res = sparql_client.post('/sparql/vocab/query',
                             {'query': test_queries.SELECT_FROM_NLP})
    assert res.status_code == 200
    assert len(res.data) == 0

    # Should ignore FROM clause if endpoint and graph don't match
    res = sparql_client.post(QUERY_URL,
                             {'query': test_queries.SELECT_FROM_SOURCES})
    assert res.status_code == 200
    assert len(res.data) == 3

    # Should return results if FROM and endpoint match
    res = sparql_client.post(QUERY_URL,
                             {'query': test_queries.SELECT_FROM_NLP})
    assert res.status_code == 200
    assert len(res.data) == 3


def test_blanknodes(blanknode_queries):
    view = SPARQLUpdateAPIView()
    for q in blanknode_queries:
        with pytest.raises(BlankNodeError):
            view.check_supported(q)


def test_GET_body(sparql_client):
    res = sparql_client.get(
        QUERY_URL,
        data={'query': 'some query'}
    )
    assert res.status_code == 400


def test_graph_negotiation(sparql_client, accept_headers, test_queries):
    ''' result headers should succeed for CONSTRUCT/DESRIBE/empty, fail for SELECT/ASK'''
    graph_headers = [accept_headers.rdfxml, accept_headers.ntriples,
                     accept_headers.jsonld, accept_headers.turtle]

    for h in graph_headers:
        accept = sparql_client.get(
            QUERY_URL, {'query': test_queries.CONSTRUCT}, HTTP_ACCEPT=h)
        deny = sparql_client.get(
            QUERY_URL, {'query': test_queries.SELECT}, HTTP_ACCEPT=h)
        empty = sparql_client.get(QUERY_URL, HTTP_ACCEPT=h)
        assert accept.status_code == 200
        assert check_content_type(accept, h)
        assert deny.status_code == 406
        assert empty.status_code == 200
        assert check_content_type(empty, h)


def test_result_negotiation(sparql_client, accept_headers, test_queries):
    ''' result headers should succeed for SELECT/ASK, fail for CONSTRUCT/DESCRIBE/empty'''
    result_headers = [accept_headers.sparql_json, accept_headers.sparql_xml,
                      accept_headers.sparql_csv]
    for h in result_headers:
        accept = sparql_client.get(
            QUERY_URL, {'query': test_queries.SELECT}, HTTP_ACCEPT=h)
        deny = sparql_client.get(
            QUERY_URL, {'query': test_queries.CONSTRUCT}, HTTP_ACCEPT=h)
        empty = sparql_client.get(QUERY_URL, HTTP_ACCEPT=h)
        assert accept.status_code == 200
        assert check_content_type(accept, h)
        assert deny.status_code == 406
        assert empty.status_code == 406

    # application/json should not work
    regular_json = sparql_client.get(
        QUERY_URL, {'query': test_queries.SELECT},
        HTTP_ACCEPT=accept_headers.json)
    assert regular_json.status_code == 406
