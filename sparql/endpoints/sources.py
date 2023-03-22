from django.urls import path

from sources import SOURCES_SLUG
from sources.graph import graph
from sparql.views import SPARQLQueryAPIView, SPARQLUpdateAPIView


class SourcesQueryView(SPARQLQueryAPIView):

    def graph(self):
        return graph()


class SourcesUpdateView(SPARQLUpdateAPIView):

    def graph(self):
        return graph()


SOURCES_URLS = [
    path('{}/query'.format(SOURCES_SLUG), SourcesQueryView.as_view()),
    path('{}/update'.format(SOURCES_SLUG), SourcesUpdateView.as_view())
]
