# restframework-rdf

A django app for integration between RDF and django rest framework.

## Quick start

To include this app in your django project, do the following.

1. Add `'rdf'` to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
    ...
    'rdf',
]
```

2. Determine the endpoint for sparql queries to your triple store. For example, if you are using blazegraph with namespace 'foo', this would be `'http://localhost:9999/blazegraph/namespace/foo/sparql'`

3. Add the following to your settings file:

```python
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

TRIPLESTORE_SPARQL_ENDPOINT = '...' # fill in the endpoint url

RDFLIB_STORE = SPARQLUpdateStore(
    query_endpoint=TRIPLESTORE_SPARQL_ENDPOINT,
    update_endpoint=TRIPLESTORE_SPARQL_ENDPOINT,
)
```

Note that you may want to use a different endpoint for unit tests.

4. Run `django rdfmigrate` to perform RDF migrations