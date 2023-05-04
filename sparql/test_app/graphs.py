from rdflib.graph import Graph
from django.conf import settings
from sparql.test_app.constants import *

def sources_graph():
    return Graph(settings.RDFLIB_STORE, SOURCES_NS)

def nlp_graph():
    return Graph(settings.RDFLIB_STORE, nlp)