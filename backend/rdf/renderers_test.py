import json

from .renderers import JSONLD_Renderer
from .ns import *

EXPECTED_JSONLD = [{
    '@id': str(RDF.type),
    '@type': [str(RDF.Property)],
    str(RDFS.range): [{'@id': str(RDFS.Class)}],
}, {
    '@id': str(RDFS.domain),
    str(RDFS.domain): [{'@id': str(RDF.Property)}],
}, {
    '@id': str(RDFS.range),
    str(RDFS.domain): [{'@id': str(RDF.Property)}],
}]


def test_rdflibrenderer(filled_graph):
    renderer = JSONLD_Renderer()
    serialization = json.loads(renderer.render(filled_graph))
    serialization.sort(key=lambda r: r['@id'])
    assert serialization == EXPECTED_JSONLD
