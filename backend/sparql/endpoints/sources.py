from django.urls import path

from sources import SOURCES_ROUTE
from sources.graph import graph
from sparql.views import SPARQLQueryAPIView


class SourcesQueryView(SPARQLQueryAPIView):
    """ Query the NLP ontology through SPARQL-Query """

    def graph(self):
        return graph()


SOURCES_URLS = [
    path('{}/query'.format(SOURCES_ROUTE), SourcesQueryView.as_view()),
]
