from rdf.renderers import (JsonLdRenderer, NTriplesRenderer, RdfXMLRenderer,
                           TurtleRenderer)
from rest_framework.negotiation import DefaultContentNegotiation

from .renderers import (QueryResultsCSVRenderer, QueryResultsJSONRenderer,
                        QueryResultsXMLRenderer)


class SPARQLContentNegotiator(DefaultContentNegotiation):
    results_renderers = [QueryResultsJSONRenderer, QueryResultsXMLRenderer,
                         QueryResultsCSVRenderer]
    rdf_renderers = [TurtleRenderer, RdfXMLRenderer,
                     JsonLdRenderer, NTriplesRenderer]
    querytype_accepts = {
        'SELECT': results_renderers,
        'ASK': results_renderers,
        'CONSTRUCT': rdf_renderers,
        'EMPTY': rdf_renderers
    }

    def select_renderer(self, request, renderers, format_suffix=None):
        query_type = request.data.get('query_type', None)
        renderer_classes = self.querytype_accepts.get(
            query_type, self.rdf_renderers + self.results_renderers)
        renderers = [renderer() for renderer in renderer_classes]

        return super().select_renderer(request, renderers, format_suffix)
