from django.conf import settings
from django.urls import path
from .views import SPARQLQueryAPIView, SPARQLUpdateAPIView
from itertools import chain

def sparql_query_view(endpoint_setting):
    '''
    Create a query view based on the setting for a SPARQL endpoint.

    Returns a subclass `SPARQLQueryAPIView that uses the configured graph object.
    '''

    graph = endpoint_setting['graph']
    class QueryView(SPARQLQueryAPIView):
        def graph(self):
            return graph()

    return QueryView

def sparql_update_view(endpoint_setting):
    '''
    Create an update view based on the setting for a SPARQL endpoint.

    Returns a subclass `SPARQLUpdateAPIView that uses the configured graph object.
    '''

    graph = endpoint_setting['graph']
    class UpdateView(SPARQLUpdateAPIView):

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

