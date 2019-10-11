from rest_framework.views import APIView
from rest_framework.response import Response

from rdf.renderers import TurtleRenderer
from rdf.parsers import JSONLDParser

class RDFView(APIView):
    """
    Expose a given graph as an RDF-encoded API endpoint.

    Either set a static `graph` member or override `get_graph` to
    compute the graph dynamically.

    For now, only Turtle output and JSON-LD input is supported.
    """
    renderer_classes = (TurtleRenderer,)
    parser_classes = (JSONLDParser,)

    def get(self, request, format=None, **kwargs):
        return Response(self.get_graph(request, **kwargs))

    def get_graph(self, request, **kwargs):
        return self.graph
