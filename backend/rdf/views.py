from rest_framework.views import APIView, exception_handler
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.exceptions import NotFound

from rdflib import Graph, URIRef, BNode, Literal

from rdf.ns import *
from rdf.renderers import TurtleRenderer
from rdf.parsers import JSONLDParser
from rdf.utils import append_triples, graph_from_triples

HTTPSC_MAP = {
    # Both Django REST framework and HTTPSC are incomplete.
    # This mapping contains only the error codes they have in common.
    HTTP_400_BAD_REQUEST: HTTPSC.BadRequest,
    HTTP_401_UNAUTHORIZED: HTTPSC.Unauthorized,
    HTTP_402_PAYMENT_REQUIRED: HTTPSC.PaymentRequired,
    HTTP_403_FORBIDDEN: HTTPSC.Forbidden,
    HTTP_404_NOT_FOUND: HTTPSC.NotFound,
    HTTP_405_METHOD_NOT_ALLOWED: HTTPSC.MethodNotAllowed,
    HTTP_406_NOT_ACCEPTABLE: HTTPSC.NotAcceptable,
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED: HTTPSC.ProxyAuthenticationRequired,
    HTTP_408_REQUEST_TIMEOUT: HTTPSC.RequestTimeout,
    HTTP_409_CONFLICT: HTTPSC.Conflict,
    HTTP_410_GONE: HTTPSC.Gone,
    HTTP_411_LENGTH_REQUIRED: HTTPSC.LengthRequired,
    HTTP_412_PRECONDITION_FAILED: HTTPSC.PreconditionFailed,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE: HTTPSC.RequestEntityTooLarge,
    HTTP_414_REQUEST_URI_TOO_LONG: HTTPSC.RequestURITooLong,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE: HTTPSC.UnsupportedMediaType,
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE: HTTPSC.RequestedRangeNotSatisfiable,
    HTTP_417_EXPECTATION_FAILED: HTTPSC.ExpectationFailed,
    HTTP_422_UNPROCESSABLE_ENTITY: HTTPSC.UnprocessableEntity,
    HTTP_423_LOCKED: HTTPSC.Locked,
    HTTP_424_FAILED_DEPENDENCY: HTTPSC.FailedDependency,
    HTTP_500_INTERNAL_SERVER_ERROR: HTTPSC.InternalServerError,
    HTTP_501_NOT_IMPLEMENTED: HTTPSC.NotImplemented,
    HTTP_502_BAD_GATEWAY: HTTPSC.BadGateway,
    HTTP_503_SERVICE_UNAVAILABLE: HTTPSC.ServiceUnavailable,
    HTTP_504_GATEWAY_TIMEOUT: HTTPSC.GatewayTimeout,
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED: HTTPSC.HTTPVersionNotSupported,
    HTTP_507_INSUFFICIENT_STORAGE: HTTPSC.InsufficientStorage,
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
        (res, HTTP.statusCodeValue, Literal(status)),
        (res, HTTP.reasonPhrase, Literal(original_data['detail'])),
    ))
    status_uri = HTTPSC_MAP.get(status)
    if status_uri:
        override_data.add((res, HTTP.sc, status_uri))
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
