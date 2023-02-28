from rest_framework.parsers import BaseParser

from rdflib import Graph


class RDFLibParser(BaseParser):
    """ Base class for RDF parsers.

    Derive from this class to create a parser for a particular RDF
    serialization format such as JSON-LD. Subclasses need not define
    any methods, but should define two static attributes.

    The first attribute is facing the Django REST Framework side of
    the equation: `media_type` (the MIME type). This is used in
    content negotiation.

    The other attribute is `rdflib_args`, which must be a dictionary
    and which should list all named arguments to Graph.parse. At the
    very least, this should include the `format` parameter, which
    determines the serialization format.
    """
    def parse(self, stream, media_type=None, parser_context=None):
        graph = Graph()
        graph.parse(data=stream.read(), **self.rdflib_args)
        return graph


class JSONLDParser(RDFLibParser):
    media_type = 'application/ld+json'
    rdflib_args = {
        'format': 'json-ld',
    }
