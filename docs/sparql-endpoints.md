# SPARQL endpoints

## Defining endpoints

To add sparql endpoints to your application, you must define them in your Django settings. Add a setting `SPARQL_ENDPOINTS` to your settings file. For each endpoint, you will need to provide the following information:

- The route for the endpoint in the application.
- The graph that the endpoint connects to.
- Whether a query endpoint should be made.
- Whether an update endpoint should be made.

These are explained in more detail below. Ultimately, you setting should be structured like so:

```python
SPARQL_ENDPOINTS = [
    {
        'route': 'foo',
        'graph': foo_graph,
        'query': True,
        'update': True,
    },
    {
        'route': 'bar',
        'graph': bar_graph,
        'query': True,
        'update': False,
    }
]
```

The _route_ should be a string. In the example above, the "foo" graph will get two endpoints: `/foo/query` and `/foo/update`. (The "bar" graph will only have `/bar/query`)

The _graph_ should be a function that creates an rdflib `Graph` object. For example:

```python
from rdflib import Graph

def foo_graph():
    return Graph(...) # specify options
```

It is recommended that you use your configured store setting (see the [getting started guide](/getting-started)) in the graph constructor: `Graph(store = settings.RDFLIB_STORE)`

The _query_ and _update_ items control whether query and update endpoints should be added, respectively. (You should set at least one of these to `True` if you want something to happen.)