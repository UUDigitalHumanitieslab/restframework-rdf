from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from rdflib import Graph, URIRef, BNode, Literal

from rdf.ns import *
from rdf.renderers import TurtleRenderer
from rdf.parsers import JSONLDParser

DOES_NOT_EXIST_404 = 'Resource does not exist.'
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


def error_response(request, status, message):
    """ Return an RDF-encoded 4xx page that includes any request data. """
    data = graph_from_request(request)
    req = BNode()
    res = BNode()
    for triple in (
        (req, RDF.type, HTTP.Request),
        (req, HTTP.mthd, HTTPM[request.method]),
        (req, HTTP.resp, res),
        (res, RDF.type, HTTP.Response),
        (res, HTTP.sc, HTTPSC_MAP[status]),
        (res, HTTP.statusCodeValue, Literal(status)),
        (res, HTTP.reasonPhrase, Literal(message)),
    ): data.add(triple)
    return Response(data, status=status)


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


class RDFResourceView(RDFView):
    """ API endpoint for fetching individual subjects. """

    def get(self, request, format=None, **kwargs):
        data = self.get_graph(request, **kwargs)
        if len(data) == 0:
            return error_response(request, HTTP_404_NOT_FOUND, DOES_NOT_EXIST_404)
        return Response(data)

    def get_graph(self, request, **kwargs):
        identifier = URIRef(self.get_resource_uri(request, **kwargs))
        result = Graph()
        for triple in self.graph().triples((identifier, None, None)):
            result.add(triple)
        # TODO: also include related nodes
        return result

    def get_resource_uri(self, request, **kwargs):
        return request.build_absolute_uri(request.path)
