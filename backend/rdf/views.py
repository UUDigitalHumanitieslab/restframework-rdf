from rest_framework.views import APIView, exception_handler
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.exceptions import NotFound

from rdflib import Graph, URIRef, BNode, Literal

from rdf.ns import *
from rdf.renderers import TurtleRenderer
from rdf.parsers import JSONLDParser
from rdf.utils import append_triples, graph_from_triples

HTTPSC_MAP = {
    HTTP_400_BAD_REQUEST: HTTPSC.BadRequest,
    HTTP_404_NOT_FOUND: HTTPSC.NotFound,
}


def graph_from_request(request):
    """ Safely obtain a graph, from the request if present, empty otherwise. """
    data = request.data
    if not isinstance(data, Graph):
        data = Graph()
    return data


def custom_exception_handler(error, context):
    """ Returns a Graph as data instead of JSON. """
    response = exception_handler(error, context)
    if response is None:
        return response
    status = response.status_code
    original_data = response.data
    res = BNode()
    override_data = graph_from_triples((
        (res, RDF.type, HTTP.Response),
        (res, HTTP.sc, HTTPSC_MAP[status]),
        (res, HTTP.statusCodeValue, Literal(status)),
        (res, HTTP.reasonPhrase, Literal(original_data['detail'])),
    ))
    response.data = override_data
    return response


class RDFView(APIView):
    """
    Expose a given graph as an RDF-encoded API endpoint.

    Either set a static `graph` member function or override
    `get_graph` to compute the graph from the request.

    For now, only Turtle output and JSON-LD input is supported.
    """
    renderer_classes = (TurtleRenderer,)
    parser_classes = (JSONLDParser,)

    def get(self, request, format=None, **kwargs):
        return Response(self.get_graph(request, **kwargs))

    def get_graph(self, request, **kwargs):
        return self.graph()

    def get_exception_handler(self):
        return custom_exception_handler


class RDFResourceView(RDFView):
    """ API endpoint for fetching individual subjects. """

    def get(self, request, format=None, **kwargs):
        data = self.get_graph(request, **kwargs)
        if len(data) == 0:
            raise NotFound()
        return Response(data)

    def get_graph(self, request, **kwargs):
        identifier = URIRef(self.get_resource_uri(request, **kwargs))
        pattern = (identifier, None, None)
        result = graph_from_triples(self.graph().triples(pattern))
        # TODO: also include related nodes
        return result

    def get_resource_uri(self, request, **kwargs):
        return request.build_absolute_uri(request.path)
