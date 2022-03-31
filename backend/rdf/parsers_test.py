from io import BytesIO

from rdflib import Graph

from .parsers import JSONLDParser
from .ns import *


def test_rdflibparser(filled_graph):
    parser = JSONLDParser()
    serialized = filled_graph.serialize(format='json-ld').encode()
    parsed = parser.parse(BytesIO(serialized))
    assert len(parsed ^ filled_graph) == 0
