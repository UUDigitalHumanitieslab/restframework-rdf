from django.urls import path

from items import ITEMS_SLUG
from items.graph import graph
from sparql.views import SPARQLQueryAPIView


class ItemsQueryView(SPARQLQueryAPIView):
    """ Query the NLP ontology through SPARQL-Query """

    def graph(self):
        return graph()


ITEMS_URLS = [
    path('{}/query'.format(ITEMS_SLUG), ItemsQueryView.as_view()),
]
