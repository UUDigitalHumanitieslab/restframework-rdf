from rest_framework.negotiation import DefaultContentNegotiation

from rdf.renderers import TurtleRenderer

from .renderers import QueryResultsJSONRenderer, QueryResultsTurtleRenderer


class SPARQLContentNegotiator(DefaultContentNegotiation):
    results_renderers = (QueryResultsJSONRenderer, QueryResultsTurtleRenderer)
    rdf_renderers = (TurtleRenderer,)

    def select_renderer(self, request, renderers, format_suffix=None):
        query_type = request.data.get('query_type', None)

        if query_type in ('ASK', 'SELECT'):
            renderers = [renderer() for renderer in self.results_renderers]
        elif query_type in ('EMPTY', 'CONSTRUCT'):
            renderers = [renderer() for renderer in self.rdf_renderers]
        else:
            renderers = [renderer() for renderer in set(
                self.rdf_renderers+self.results_renderers)]

        return super().select_renderer(request, renderers, format_suffix)
