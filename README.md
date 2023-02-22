# restframework-rdf

A django app for integration between RDF and django rest framework.

## Quick start

To include this app in your django project, install the package via pip, then do the following.

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

## Development and unit tests

These steps are for development on the rdf app itself. Follow the steps below in order to run the unit tests.

### Blazegraph

Before you start, you need to install [Blazegraph](http://blazegraph.com/). The unit tests assume that you have a blazegraph server running and that the namespace 'rdf-test' is created. The following steps suffice to make this true.

Follow the [Blazegraph quick start guide](https://github.com/blazegraph/database/wiki/Quick_Start) to download and start the database server and a foreground process.
While the server is running, you can access its web interface at http://localhost:9999. This lets you upload and download data, try out queries and review statistics about the dataset. The server can be stopped by typing `ctrl-c`.
Visit the [web interface]( http://localhost:9999), navigate to the `NAMESPACES` tab. Use the `create namespace` form to create a new namespace. Choose `rdf-test` as a name, and set the mode to `quads`. All other checkboxes should be disabled. A popup is shown with additional settings. Leave these at their default values and choose `Create`. The created namespace should now appear in the list of namespaces. Choose `use` to use the rdf-test namespace when operating the web interface

### Running unit tests

1. Clone this repository
2. Install the required python packages via `pip install -r requirements.in`
3. Make sure your blazegraph server is running (see above).
4. Run the unit tests with `pytest`.

### Usage during development

To use your work-in-progress drf app in a django project, build the package with

```bash
python setup.py sdist
```

You can now find the package in this repository under `dist/restframework-drf-blablabla.tar.gz`

To install the package in your project, install via pip as 

```bash
pip install path/to/repository/dist/restframework-drf-*.targ.gz
```
