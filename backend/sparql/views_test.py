import json

from rdflib import Graph

QUERY_URL = '/sparql/nlp-ontology/query'
UPDATE_URL = '/sparql/nlp-ontology/update'


def check_content_type(response, content_type):
    return content_type in response._headers['content-type'][1]


def results_as_dict(data):
    return json.loads(data.decode('utf8'))


def queryresult_count(data):
    decoded = results_as_dict(data)
    return len(decoded['results']['bindings'])


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


def test_from_query(sparql_client, test_queries, sparqlstore):
    other_graph_url = '/sparql/source/query'

    # Put some data into nlp_ontology graph
    sparql_client.post(UPDATE_URL, {'update': test_queries.INSERT})

    # Query to nlp_ontology should return the inserted triples
    res = sparql_client.get(QUERY_URL)
    data = Graph().parse(data=res.content, format='turtle')
    assert res.status_code == 200
    assert len(data) == 3

    # Query to another graph should return no triples
    res_other = sparql_client.get(other_graph_url)
    data_other = Graph().parse(data=res_other.content, format='turtle')
    assert res_other.status_code == 200
    assert len(data_other) == 0

    # FROM <another_graph> query should return the triples in nlp_ontology
    res_from = sparql_client.post(
        QUERY_URL, {'query': test_queries.SELECT_FROM})
    data_from = json.loads(res_from.content.decode('utf8'))['results']
    assert res_from.status_code == 200
    assert len(data_from['bindings']) == 3


def test_clear(sparql_client, test_queries, sparqlstore, accept_headers):
    other_query = '/sparql/ontology/query'
    other_update = '/sparql/ontology/update'

    g1 = sparql_client.get(QUERY_URL, {'query': test_queries.SELECT}).content
    g2 = sparql_client.get(other_query, {'query': test_queries.SELECT}).content
    assert queryresult_count(g1) == queryresult_count(g2) == 0

    sparql_client.post(UPDATE_URL, {'update': test_queries.INSERT})
    sparql_client.post(other_update, {'update': test_queries.INSERT})
    g1 = sparql_client.get(QUERY_URL, {'query': test_queries.SELECT}).content
    g2 = sparql_client.get(other_query, {'query': test_queries.SELECT}).content
    assert queryresult_count(g1) == queryresult_count(g2) == 3

    sparql_client.post(
        UPDATE_URL, {'update': 'CLEAR GRAPH <http://testserver/nlp-ontology#>'})
    g1 = sparql_client.get(QUERY_URL, {'query': test_queries.SELECT}).content
    g2 = sparql_client.get(other_query, {'query': test_queries.SELECT}).content
    assert queryresult_count(g1) == 0
    assert queryresult_count(g2) == 3

    # CLEAR other graph to specified endpoint should not work
    # currently fails
    sparql_client.post(
        UPDATE_URL, {'update': 'CLEAR GRAPH <http://testserver/ontology#>'})
    g2 = sparql_client.get(other_query, {'query': test_queries.SELECT}).content
    assert queryresult_count(g2) == 3

    # CLEAR ALL to specified endpoint should not clear others
    # currently fails (also after removing test above)
    client.post(
        UPDATE_URL, {'update': 'CLEAR ALL'})
    g2 = client.get(other_query, {'query': test_queries.SELECT}).content
    assert queryresult_count(g2) == 3
