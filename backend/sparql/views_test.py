import json

from rdflib import Graph

QUERY_URL = '/sparql/nlp-ontology/query'
UPDATE_URL = '/sparql/nlp-ontology/update'


def check_content_type(response, content_type):
    return content_type in response._headers['content-type'][1]


def test_insert(admin_client, ontologygraph_db, test_queries):
    post_response = admin_client.post(
        UPDATE_URL, {'update': test_queries.INSERT})
    assert post_response.status_code == 200

    get_response = admin_client.get(QUERY_URL)
    assert get_response.status_code == 200
    assert check_content_type(get_response, 'text/turtle')

    get_data = Graph()
    get_data.parse(data=get_response.content, format='turtle')
    assert len(get_data) == 3


def test_ask(client, test_queries, ontologygraph_db):
    true_response = client.get(
        QUERY_URL, {'query': test_queries.ASK_TRUE})
    assert true_response.status_code == 200
    assert json.loads(true_response.content)['boolean']
    assert check_content_type(true_response, 'application/sparql-results+json')

    false_response = client.get(
        QUERY_URL, {'query': test_queries.ASK_FALSE})
    assert false_response.status_code == 200
    assert not json.loads(false_response.content)['boolean']


def test_construct(client, test_queries, ontologygraph_db):
    response = client.get(QUERY_URL, {'query': test_queries.CONSTRUCT})
    assert response.status_code == 200


def test_authorized(admin_client, test_queries):
    response = admin_client.post(UPDATE_URL, {'update': test_queries.INSERT})
    assert response.status_code == 200


def test_unauthorized(client):
    response = client.post(UPDATE_URL)
    assert response.status_code == 403


def test_malformed_update(admin_client):
    response = admin_client.post(
        UPDATE_URL, {'update': 'this is no SPARQL update!'})
    assert response.status_code == 400


def test_malformed_query(admin_client):
    response = admin_client.post(
        QUERY_URL, {'query': 'this is no SPARQL query!'})
    assert response.status_code == 400


def test_negotiation(client, ontologygraph_db):
    empty_get = client.get(QUERY_URL)
    assert empty_get.status_code == 200
    assert check_content_type(empty_get, 'text/turtle')
