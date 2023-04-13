from rdflib.graph import Graph
from django.conf import settings
from rdflib import Namespace

SOURCES_NS = Namespace('{}{}#'.format('http://testserver/', 'source/'))

def graph():
    return Graph(settings.RDFLIB_STORE, SOURCES_NS)