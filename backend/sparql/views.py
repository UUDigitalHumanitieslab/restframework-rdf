import re
import logging

from django.http.response import HttpResponseBase
from pyparsing import ParseException
from rdf.ns import HTTP, HTTPSC, RDF
from rdf.renderers import TurtleRenderer
from rdf.utils import graph_from_triples
from rdf.views import custom_exception_handler as turtle_exception_handler
from rdflib import BNode, Literal
from rdflib.plugins.sparql.parser import parseUpdate
from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException, NotAcceptable, ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import (BLANK_NODE_PATTERN, UPDATE_NOT_SUPPORTED,
                        UPDATE_NOT_SUPPORTED_PATTERN)
from .exceptions import (BlankNodeError, NoParamError, ParseSPARQLError,
                         UnsupportedUpdateError)
from .negotiation import SPARQLContentNegotiator
from .permissions import SPARQLPermission

logger = logging.getLogger(__name__)


class SPARQLUpdateAPIView(APIView):
    renderer_classes = (TurtleRenderer,)
    permission_classes = (SPARQLPermission,)

    def get_exception_handler(self):
        return turtle_exception_handler

    def check_supported(self, updatestring):
        logger.debug('enter SPARQLUpdateAPIView.check_supported')
        # check the entire string for unsupported keywords
        if re.match(UPDATE_NOT_SUPPORTED_PATTERN, updatestring):
            logger.debug('UPDATE_NOT_SUPPORTED_PATTERN matched')
            # do a dry-run parse of the updatestring
            parse_request = parseUpdate(updatestring).request
            # check if the parse contains any unsupported operations
            if any(part.name in UPDATE_NOT_SUPPORTED for part in parse_request):
                logger.debug('unsupported operation confirmed')
                raise UnsupportedUpdateError(
                    'Update operation is not supported.'
                )

        # Do a quick check for blank nodes
        if re.search(BLANK_NODE_PATTERN, updatestring):
            logger.debug('BLANK_NODE_PATTERN matched')
            parse_request = parseUpdate(updatestring).request
            for part in parse_request:
                if any(
                        isinstance(term, BNode)
                        for triple in part.quads.triples
                        for term in triple
                ):
                    logger.debug('blank node confirmed')
                    raise BlankNodeError()

        logger.debug('exit SPARQLUpdateAPIView.check_supported')
        return

    def execute_update(self, updatestring):
        logger.debug('enter SPARQLUpdateAPIView.execute_update')
        graph = self.graph()

        try:
            self.check_supported(updatestring)
            logger.debug('graph size before update: %d', len(graph))
            graph.update(updatestring)
            logger.debug('graph size after update: %d', len(graph))
        except (ParseException, ParseError) as p_e:
            # Raised when SPARQL syntax is not valid, or parsing fails
            graph.rollback()
            logger.exception('parse error')
            raise ParseSPARQLError(p_e)
        except HTTPError as h_e:
            graph.rollback()
            if 400 <= h_e.response.status_code < 500:
                logger.exception('parse error on remote server')
                raise ParseSPARQLError(h_e)
            else:
                logger.exception('internal error on remote server')
                raise APIException(h_e)
        except Exception as e:
            graph.rollback()
            logger.exception('another error')
            raise APIException(e)
        logger.debug('exit SPARQLUpdateAPIView.execute_update')

    def post(self, request, **kwargs):
        """ Accepts POST request with SPARQL-Query in body parameter 'query'
            Renders text/turtle
        """
        logger.debug('enter SPARQLUpdateAPIView.post (%s)', request.build_absolute_uri())
        sparql_string = request.data.get("update")
        if not sparql_string:
            # POST must contain an update
            logger.debug('no query update string')
            raise NoParamError()
        logger.debug('query update string:\n %s', sparql_string)
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
        logger.debug('returning from SPARQLUpdateAPIView.post')
        return Response(response)

    def graph(self):
        raise NotImplementedError


class SPARQLQueryAPIView(APIView):
    renderer_classes = SPARQLContentNegotiator.rdf_renderers + \
        SPARQLContentNegotiator.results_renderers
    content_negotiation_class = SPARQLContentNegotiator

    def get_exception_handler(self):
        ''' Errors are returned as turtle, even when the original querytype
        does not satisfy could not be rendered in this format. A hard
        overwrite of renderer is necessary. Ideally, this should render errors
        in a querytype-compatibleway. '''
        self.request.accepted_renderer = TurtleRenderer()
        self.request.accepted_media_type = TurtleRenderer.media_type
        return turtle_exception_handler

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

            # re-perform content negotiation to determine if
            # querytype satisfies accept header
            neg = self.perform_content_negotiation(self.request)
            self.request.accepted_renderer, self.request.accepted_media_type = neg
            return query_results

        except ParseException as p_e:
            # Raised when SPARQL syntax is not valid, or parsing fails
            graph.rollback()
            raise ParseSPARQLError(p_e)
        except HTTPError as h_e:
            graph.rollback()
            if 400 <= h_e.response.status_code < 500:
                raise ParseSPARQLError(h_e)
            else:
                raise APIException(h_e)
        except NotAcceptable:
            graph.rollback()
            raise
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
        if request.data:
            raise ParseSPARQLError(
                "GET request should provide query in parameter, not request body.")
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
