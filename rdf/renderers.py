from rest_framework.renderers import BaseRenderer


class RDFLibRenderer(BaseRenderer):
    """ Base class for RDF renderers.

    Derive from this class to create a renderer for a particular RDF
    serialization format such as JSON-LD. Subclasses need not define
    any methods, but should define two groups of static attributes.

    The first group is facing the Django REST Framework side of the
    equation. These are the same attributes that all BaseRenderer
    subclasses should define: `media_type` (the MIME type), `format`
    (an extension that may be append to the request path as an
    alternative means of content negotiation) and optionally `charset`.
    They are used in content negotiation.

    The other group is the single `rdflib_args` attribute, which must
    be a dictionary and which should list all named arguments to
    Graph.serialize. At the very least, this should include the
    `format` parameter, which determines the serialization format.
    """

    def render(self, graph, media_type=None, renderer_context=None):
        view = None
        if renderer_context is not None and 'view' in renderer_context:
            view = renderer_context['view']
        rdflib_args = self.get_rdflib_args(view=view)
        return graph.serialize(**rdflib_args)

    def get_rdflib_args(self, **kwargs):
        return self.rdflib_args


class TurtleRenderer(RDFLibRenderer):
    media_type = 'text/turtle'
    format = 'ttl'
    rdflib_args = {
        'format': 'turtle',
    }


class RdfXMLRenderer(RDFLibRenderer):
    media_type = 'application/rdf+xml'
    format = 'xml'
    rdflib_args = {
        'format': 'xml',
    }


class JsonLdRenderer(RDFLibRenderer):
    media_type = 'application/ld+json'
    format = 'jsonld'
    json_ld_context = None

    def get_rdflib_args(self, view=None):
        args = {
            'format': 'json-ld',
        }
        if (
                hasattr(view, "json_ld_context")
                and view.json_ld_context is not None
        ):
            args['context'] = view.json_ld_context
        return args


class NTriplesRenderer(RDFLibRenderer):
    media_type = 'application/n-triples'
    format = 'nt'
    rdflib_args = {
        'format': 'nt',
        'encoding': 'ascii'  # N-triples are always ascii encoded
    }
