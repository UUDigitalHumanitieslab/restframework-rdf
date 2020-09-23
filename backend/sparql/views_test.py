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


def test_clear_self_other(sparql_client, query_with_results, sparqlstore):
    other_query = '/sparql/source/query'
    other_update = '/sparql/source/update'

    ins = query_with_results.insert
    sel = query_with_results.select
    exp = query_with_results.expected
    empty = query_with_results.empty

    # Insert the same data on two endpoints
    post1 = sparql_client.post(UPDATE_URL, {'update': ins})
    post2 = sparql_client.post(other_update, {'update': ins})
    assert post1.status_code == post2.status_code == 200

    # Assert data at both endpoints is equal
    g1 = sparql_client.get(QUERY_URL, {'query': sel}).content
    g2 = sparql_client.get(other_query, {'query': sel}).content
    assert results_as_dict(g1) == results_as_dict(g2) == exp

    # Clear self
    clear_self = sparql_client.post(
        UPDATE_URL, {'update': query_with_results.clear_self})
    g1 = sparql_client.get(QUERY_URL, {'query': sel}).content
    assert clear_self.status_code == 200
    assert results_as_dict(g1) == empty

    # Clear other
    clear_other = sparql_client.post(
        UPDATE_URL, {'update': query_with_results.clear_other})
    g2 = sparql_client.get(other_query, {'query': sel}).content
    assert clear_other.status_code == 200
    assert results_as_dict(g2) == exp
