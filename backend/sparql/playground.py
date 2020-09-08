ns = 'http://testserver/source/'

SELECT_FROM_QUERY = '''
    SELECT ?s ?p ?o
    FROM <{ns}>
    WHERE {{
        ?s ?p ?o .
    }}
'''.format(ns=ns)

print(SELECT_FROM_QUERY)


{'bindings': [{'s': {'type': 'uri', 'value': 'http://schema.org/Cat'}, 'p': {'type': 'uri', 'value': 'http://testserver/nlp-ontology#meow'}, 'o': {'type': 'literal', 'value': 'loud'}}, {'s': {'type': 'uri', 'value': 'http://testserver/nlp-ontology#icecream'}, 'p': {'type': 'uri',
                                                                                                                                                                                                                                                                          'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, 'o': {'type': 'uri', 'value': 'http://schema.org/Food'}}, {'s': {'type': 'uri', 'value': 'http://testserver/nlp-ontology#icecream'}, 'p': {'type': 'uri', 'value': 'http://schema.org/color'}, 'o': {'type': 'literal', 'value': '#f9e5bc'}}]}
