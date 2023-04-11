# Getting started

## Installation

Install the restframework-rdf package via pip.

```bash
pip install restframework-drf
```

## Django project configuration

To include this app in your django project, do the following.

Add `'rdf'` to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
    ...
    'rdf',
]
```

Determine the endpoint for sparql queries to your triple store. For example, if you are using blazegraph with namespace 'foo' in local development, the endpoint for both querying and updating would be `'http://localhost:9999/blazegraph/namespace/foo/sparql'`

Add the following to your settings file:

```python
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

TRIPLESTORE_SPARQL_QUERY_ENDPOINT = '...' # fill in the endpoint url
TRIPLESTORE_SPARQL_UPDATE_ENDPOINT = '...' # fill in the endpoint url

RDFLIB_STORE = SPARQLUpdateStore(
    query_endpoint=TRIPLESTORE_SPARQL_QUERY_ENDPOINT,
    update_endpoint=TRIPLESTORE_SPARQL_UPDATE_ENDPOINT,
)
```

Note that you may want to use a different endpoint for unit tests.
