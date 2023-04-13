from django.conf import settings
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

def pytest_configure():
    triplestore_namespace = 'rdf-test'
    triplestore_sparql_endpoint = f'http://localhost:9999/blazegraph/namespace/{triplestore_namespace}/sparql'

    settings.configure(
        SECRET_KEY='secret',
        INSTALLED_APPS = [
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.contenttypes',
        ],
        REST_FRAMEWORK = {},
        RDF_NAMESPACE_ROOT = 'http://localhost:8000/',
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'rdf-test',
            }
        },
        RDFLIB_STORE = SPARQLUpdateStore(
            query_endpoint=triplestore_sparql_endpoint,
            update_endpoint=triplestore_sparql_endpoint,
        ),

    )