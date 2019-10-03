from rest_framework.views import APIView
from rest_framework.response import Response

from rdf.renderers import JSONLD_Renderer

class RDFView(APIView):
    """
    Expose a given graph as an RDF-encoded API endpoint.

    Either set a static `graph` member or override `get_graph` to
    compute the graph dynamically.

    For now, only json-ld is supported.
    """
    renderer_classes = (JSONLD_Renderer,)

    def get(self, request, format=None):
        return Response(self.get_graph(request))

    def get_graph(self, request):
        return self.graph
