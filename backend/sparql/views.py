import re

from django.http.response import HttpResponseBase
from pyparsing import ParseException
from rdflib import BNode, Literal
from rdflib.plugins.sparql.parser import parseUpdate
from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

from rdf.ns import HTTP, HTTPSC, RDF
from rdf.renderers import TurtleRenderer
from rdf.utils import graph_from_triples
from rdf.views import custom_exception_handler as turtle_exception_handler

from .constants import UPDATE_NOT_SUPPORTED, UPDATE_NOT_SUPPORTED_PATTERN
from .exceptions import NoParamError, NotSupportedSPARQLError, ParseSPARQLError
from .negotiation import SPARQLContentNegotiator
from .permissions import SPARQLPermission


class SPARQLUpdateAPIView(APIView):
    renderer_classes = (TurtleRenderer,)
    permission_classes = (SPARQLPermission,)

    def get_exception_handler(self):
        return turtle_exception_handler

    def is_supported(self, updatestring):
        # check the entire string for unsupported keywords
        if re.match(UPDATE_NOT_SUPPORTED_PATTERN, updatestring):
            # do a dry-run parse of the updatestring
            parse_request = parseUpdate(updatestring).request
            # check if the parse contains any unsupported operations
            for part in parse_request:
                if part.name in UPDATE_NOT_SUPPORTED:
                    return False
        return True

    def execute_update(self, updatestring):
        graph = self.graph()

        if not self.is_supported(updatestring):
            raise NotSupportedSPARQLError('Update operation is not supported.')

        # TODO: should we support? (probably not)
        # LOAD, CLEAR, DROP, ADD, MOVE, COPY, CREATE
        try:
            return graph.update(updatestring)
        except (ParseException, QueryBadFormed) as p_e:
            # Raised when SPARQL syntax is not valid, or parsing fails
            graph.rollback()
            raise ParseSPARQLError(p_e)
        except HTTPError as h_e:
            graph.rollback()
            if 400 <= h_e.response.status_code < 500:
                raise ParseSPARQLError(h_e)
            else:
                raise APIException(h_e)
        except Exception as e:
            graph.rollback()
            raise APIException(e)

    def post(self, request, **kwargs):
        """ Accepts POST request with SPARQL-Query in body parameter 'query'
            Renders text/turtle
        """
        sparql_string = request.data.get("update")
        if not sparql_string:
            # POST must contain an update
            raise NoParamError()

        blank = BNode()
        status = 200
        response = graph_from_triples(
            (
                (blank, RDF.type, HTTP.Response),
                (blank, HTTP.statusCodeValue, Literal(status)),
                (blank, HTTP.reasonPhrase, Literal("Updated successfully")),
                (blank, HTTP.sc, HTTPSC.OK),
            )
        )

        self.execute_update(sparql_string)
        return Response(response)

    def graph(self):
        raise NotImplementedError


class SPARQLQueryAPIView(APIView):
    renderer_classes = (TurtleRenderer,)
    content_negotiation_class = SPARQLContentNegotiator

    def get_exception_handler(self):
        return turtle_exception_handler

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Adapts APIView method to additionaly perform content negotation
        when a query type was set
        """
        assert isinstance(response, HttpResponseBase), (
            "Expected a `Response`, `HttpResponse` or `HttpStreamingResponse` "
            "to be returned from the view, but received a `%s`" % type(
                response)
        )

        if isinstance(response, Response):
            # re-perform content negotiation if a query type was set
            if not getattr(request, "accepted_renderer", None) or \
                    self.request.data.get("query_type", None):
                neg = self.perform_content_negotiation(request, force=True)
                request.accepted_renderer, request.accepted_media_type = neg

            response.accepted_renderer = request.accepted_renderer
            response.accepted_media_type = request.accepted_media_type
            response.renderer_context = self.get_renderer_context()

        for key, value in self.headers.items():
            response[key] = value

        return response

    def execute_query(self, querystring):
        """ Attempt to query a graph with a SPARQL-Query string
            Sets query type on succes
        """
        graph = self.graph()
        try:
            if not querystring:
                query_results = graph
                query_type = "EMPTY"
            else:
                query_results = graph.query(querystring)
                query_type = query_results.type
            self.request.data["query_type"] = query_type
            return query_results

        except (ParseException, QueryBadFormed) as p_e:
            # Raised when SPARQL syntax is not valid, or parsing fails
            graph.rollback()
            raise ParseSPARQLError(p_e)
        except HTTPError as h_e:
            graph.rollback()
            if 400 <= h_e.response.status_code < 500:
                raise ParseSPARQLError(h_e)
            else:
                raise APIException(h_e)
        except Exception as n_e:
            graph.rollback()
            raise APIException(n_e)

    def get(self, request, **kwargs):
        """ Accepts GET request, optional SPARQL-Query
            in query parameter 'query'.
            Without 'query' parameter, returns the entire graph as text/turtle.
            Renders application/json or text/turtle based
            on query type and header 'Accept.
        """
        sparql_string = request.query_params.get("query")
        query_results = self.execute_query(sparql_string)

        return Response(query_results)

    def post(self, request, **kwargs):
        """ Accepts POST request with SPARQL-Query in body parameter 'query'.
            Renders application/json or text/turtle based
            on query type and header 'Accept'.
        """
        sparql_string = request.data.get("query")
        if not sparql_string:
            raise NoParamError()
        # request.data is immutable for POST requests
        request.data._mutable = True
        query_results = self.execute_query(sparql_string)

        return Response(query_results)

    def graph(self):
        raise NotImplementedError
