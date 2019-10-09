from rdflib import Graph

from .renderers import TurtleRenderer
from .ns import *


def test_rdflibrenderer(filled_graph):
    renderer = TurtleRenderer()
    serialization = renderer.render(filled_graph)
    parsed = Graph()
    parsed.parse(data=serialization, format='turtle')
    assert len(parsed ^ filled_graph) == 0
