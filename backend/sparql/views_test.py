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
    admin_client.post(
        UPDATE_URL, {'update': 'CLEAR ALL'})


def test_ask(client, test_queries, ontologygraph_db):
    true_response = client.get(
        QUERY_URL, {'query': test_queries.ASK_TRUE})
    assert true_response.status_code == 200
    assert json.loads(true_response.content.decode('utf8'))['boolean']
    assert check_content_type(true_response, 'application/sparql-results+json')

    false_response = client.get(
        QUERY_URL, {'query': test_queries.ASK_FALSE})
    assert false_response.status_code == 200
    assert not json.loads(false_response.content.decode('utf8'))['boolean']


def test_construct(client, test_queries, ontologygraph_db):
    response = client.get(QUERY_URL, {'query': test_queries.CONSTRUCT})
    assert response.status_code == 200


def test_malformed(sparql_client, sparqlstore):
    malformed_get = sparql_client.post(
        QUERY_URL, {'query': 'this is no SPARQL query!'})
    assert malformed_get.status_code == 400

    malformed_update = sparql_client.post(
        UPDATE_URL, {'update': 'this is no SPARQL query!'})
    assert malformed_update.status_code == 400


def test_negotiation(client, ontologygraph_db, accept_headers, test_queries):
    empty_get = client.get(QUERY_URL)
    assert empty_get.status_code == 200
    assert check_content_type(empty_get, accept_headers.turtle)

    sparql_json_get = client.get(
        QUERY_URL, {'query': test_queries.SELECT},
        HTTP_ACCEPT=accept_headers.sparql_json)
    assert sparql_json_get.status_code == 200
    assert check_content_type(sparql_json_get, accept_headers.sparql_json)

    sparql_xml_get = client.get(
        QUERY_URL, {'query': test_queries.SELECT},
        HTTP_ACCEPT=accept_headers.sparql_xml)
    assert sparql_xml_get.status_code == 200
    assert check_content_type(sparql_xml_get, accept_headers.sparql_xml)

    json_get = client.get(
        QUERY_URL, {'query': test_queries.SELECT},
        HTTP_ACCEPT=accept_headers.json)
    assert json_get.status_code == 406


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


def test_delete(sparql_client, test_queries, ontologygraph_db):
    # Should not delete if from another endpoint
    delete = sparql_client.post(
        '/sparql/ontology/update', {'update': test_queries.DELETE_FROM})
    assert delete.status_code == 200
    g = sparql_client.get(QUERY_URL).content
    assert len(Graph().parse(data=g, format='turtle')) == 3

    # Should delete if endpoint and graph match
    delete = sparql_client.post(
        UPDATE_URL, {'update': test_queries.DELETE})
    assert delete.status_code == 200
    g = sparql_client.get(QUERY_URL).content
    assert len(Graph().parse(data=g, format='turtle')) == 2
