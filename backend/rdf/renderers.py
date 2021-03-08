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
        return graph.serialize(**self.rdflib_args)


class TurtleRenderer(RDFLibRenderer):
    media_type = 'text/turtle'
    format = 'ttl'
    rdflib_args = {
        'format': 'turtle',
    }
