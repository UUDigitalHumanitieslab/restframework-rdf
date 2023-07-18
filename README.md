[![Documentation Status](https://readthedocs.org/projects/restframework-rdf/badge/?version=latest)](https://restframework-rdf.readthedocs.io/en/latest/?badge=latest)
      
# restframework-rdf

Django apps for integration between Resource Description Framework (RDF) and [django REST framework](https://www.django-rest-framework.org/). The repository contains two django apps, `rdf` for general RDF functionality and `sparql` to add views for SPARQL queries. The functionality is intended as generic and useful for any project that intends to expose an RDF database through a django REST framework API.

These apps were originally developed within the [read-it interface](https://github.com/UUDigitalHumanitieslab/readit-interface). The code was moved to this independent repository so it could be used in another application, [EDPOP](https://github.com/UUDigitalHumanitieslab/EDPOP).

Both of these applications are in active development; as such, this repository may see further updates to serve the needs of different applications. We welcome contributions to make the package more widely applicable.

However, be advised that this repository was primarily developed to be used in our own applications. It may not have the level of documentation that you would expect from a public-facing package. At the very least, the documentation will assume that you have basic familiarity with both RDF and django REST framework. 

## Quick start

Follow the [getting started guide](/docs/getting-started.md) to use the app in a django project.

Usage documentation is available in the [documentation directory](/docs/) or [read the docs](https://restframework-rdf.readthedocs.io/en/latest/getting-started/)

## Development and unit tests

These steps are for development on the rdf app itself. Follow the steps below in order to run the unit tests.

### Blazegraph

Before you start, you need to install [Blazegraph](http://blazegraph.com/). The unit tests assume that you have a blazegraph server running and that the namespace 'rdf-test' is created. The following steps suffice to make this true.

Follow the [Blazegraph quick start guide](https://github.com/blazegraph/database/wiki/Quick_Start) to download and start the database server and a foreground process.
While the server is running, you can access its web interface at http://localhost:9999. This lets you upload and download data, try out queries and review statistics about the dataset. The server can be stopped by typing `ctrl-c`.
Visit the [web interface]( http://localhost:9999), navigate to the `NAMESPACES` tab. Use the `create namespace` form to create a new namespace. Choose `rdf-test` as a name, and set the mode to `quads`. All other checkboxes should be disabled. A popup is shown with additional settings. Leave these at their default values and choose `Create`. The created namespace should now appear in the list of namespaces. Choose `use` to use the rdf-test namespace when operating the web interface

### Running unit tests

1. Clone this repository
2. Install the required python packages via `pip install -r requirements.txt`
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

### Documentation

Documentation (in the `docs` directory) is based on [MkDocs](https://www.mkdocs.org/).

You can browse the documentation in a development server by running

```bash
mkdocs serve
```

