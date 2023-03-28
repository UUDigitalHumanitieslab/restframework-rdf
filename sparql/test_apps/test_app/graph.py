from rdflib.graph import Graph
from django.conf import settings

def graph():
    return Graph(store=settings.RDFLIB_STORE)