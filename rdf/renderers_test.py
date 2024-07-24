import json

from rdflib import Graph
from rest_framework.renderers import BaseRenderer

from .renderers import TurtleRenderer, JsonLdRenderer
from .ns import *
from .views import RDFView


def verify_serialization(serialization, graph: Graph, format: str) -> bool:
    parsed = Graph()
    parsed.parse(data=serialization, format=format)
    return len(parsed ^ graph) == 0


def test_rdflibrenderer(filled_graph):
    renderer = TurtleRenderer()
    serialization = renderer.render(filled_graph)
    assert verify_serialization(serialization, filled_graph, "turtle")


def test_jsonldrenderer_no_context_arg(filled_graph):
    # Using the JsonLdRenderer with no context argument at all should work
    renderer = JsonLdRenderer()
    serialization = renderer.render(filled_graph)
    assert verify_serialization(serialization, filled_graph, "json-ld")


def test_jsonldrenderer_no_jsonld_context(filled_graph):
    view = RDFView()
    view.json_ld_context = None
    renderer = JsonLdRenderer()
    context = {"view": view}
    serialization = renderer.render(filled_graph, renderer_context=context)
    assert verify_serialization(serialization, filled_graph, "json-ld")


def test_jsonldrenderer_with_jsonld_context(filled_graph):
    # Note that this test does not check if the JSON-LD context is correctly
    # applied - we assume that rdflib does this correctly.
    view = RDFView()
    view.json_ld_context = {
        "schema": "https://schema.org/",
    }
    renderer = JsonLdRenderer()
    context = {"view": view}
    serialization = renderer.render(filled_graph, renderer_context=context)
    ser_dict = json.loads(serialization)
    assert isinstance(ser_dict, dict)
    assert "@context" in ser_dict
    assert verify_serialization(serialization, filled_graph, "json-ld")

