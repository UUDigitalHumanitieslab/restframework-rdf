import json
from io import StringIO

from rdflib.plugins.sparql.results.jsonresults import JSONResultSerializer
from rest_framework.renderers import JSONRenderer

from rdf.renderers import TurtleRenderer, RDFLibRenderer
from rdf.utils import graph_from_triples


class QueryResultsTurtleRenderer(TurtleRenderer):
    ''' Renders turtle from rdflib SPARQL query results'''

    def render(self, query_results, media_type=None, renderer_context=None):
        results_graph = graph_from_triples(query_results)
        return super().render(results_graph, media_type, renderer_context)


class QueryResultsJSONRenderer(JSONRenderer):
    ''' Renders SPARQL Query Results JSON Format from rdflib query results'''
    media_type = 'application/sparql-results+json'
    format = 'srj'

    def render(self, query_results, media_type=None, renderer_context=None):
        with StringIO() as stream:
            JSONResultSerializer(query_results).serialize(stream)
            json_str = stream.getvalue()
            serialized_results = json.loads(json_str)
            return super().render(serialized_results,
                                  media_type,
                                  renderer_context)


class QueryResultsXMLRenderer(RDFLibRenderer):
    media_type = 'application/sparql-results+xml'
    format = 'xml'

    def render(self, query_results, media_type=None, renderer_context=None):
        return query_results.serialize(format='xml')
