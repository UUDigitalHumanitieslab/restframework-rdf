from django.conf import settings
from django.urls import path
from .views import SPARQLQueryAPIView, SPARQLUpdateAPIView
from itertools import chain
from django.core.exceptions import ImproperlyConfigured
from importlib import import_module

def import_object(name):
    '''
    Given a name like 'foo.bar.baz', import the object named 'baz' from module 'foo.bar'
    '''
    parts = name.split('.')
    if '.' not in name:
        raise ImproperlyConfigured(
            f'The path to graph "{name}" should at least contain a module and an object name'
        )
    module_name = '.'.join(parts[:-1])
    object_name = parts[-1]
    module = import_module(module_name)
    module.__
    return getattr(module, object_name)


def import_graph(endpoint_setting):
    '''Import the graph object based on the endpoint setting'''
    name = endpoint_setting['graph']
    return import_object(name)

def import_permissions(endpoint_setting, action):
    '''Import permissions based on an endpoint setting. Parameter `action` 
    should be either `'update'` or `'query'`, and determines whether to import 
    permissions from `'update_permissions'` or `'query_permissions'`, respectively.
    '''
    key = f'{action}_permissions'
    names = endpoint_setting.get(key, None) or []
    return [import_object(name) for name in names]

def sparql_query_view(endpoint_setting):
    '''
    Create a query view based on the setting for a SPARQL endpoint.

    Returns a subclass `SPARQLQueryAPIView that uses the configured graph object.
    '''

    graph = import_graph(endpoint_setting)
    permissions = import_permissions(endpoint_setting, 'query')

    class QueryView(SPARQLQueryAPIView):
        permission_classes = permissions
        def graph(self):
            return graph()

    return QueryView

def sparql_update_view(endpoint_setting):
    '''
    Create an update view based on the setting for a SPARQL endpoint.

    Returns a subclass `SPARQLUpdateAPIView that uses the configured graph object.
    '''

    graph = import_graph(endpoint_setting)
    permissions = import_permissions(endpoint_setting, 'update')

    class UpdateView(SPARQLUpdateAPIView):
        permission_classes = permissions

        def graph(self):
            return graph()

    return UpdateView

def sparql_query_url(endpoint_setting):
    '''
    Create a query view based on the setting for a SPARQL endpoint.

    Returns a django `path` for the query endpoint.
    '''
    
    route = endpoint_setting['route']
    view = sparql_query_view(endpoint_setting)
    return path('{}/query'.format(route), view.as_view())

def sparql_update_url(endpoint_setting):
    '''
    Create an update view based on the setting for a SPARQL endpoint.

    Returns a django `path` for the update endpoint.
    '''

    route = endpoint_setting['route']
    view = sparql_update_view(endpoint_setting)
    return path('{}/query'.format(route), view.as_view())

def sparql_endpoint_urls(endpoint_setting):
    '''
    Returns a generator of urls for the given endpoint setting.    
    '''

    if endpoint_setting['query']:
        yield sparql_query_url(endpoint_setting)
    if endpoint_setting['update']:
        yield sparql_update_url(endpoint_setting)


'''Generator of all urls based on the SPARQL_ENDPOINTS setting.'''
SPARQL_URLS = chain(
    sparql_endpoint_urls(setting) for setting in settings.SPARQL_ENDPOINTS
)

