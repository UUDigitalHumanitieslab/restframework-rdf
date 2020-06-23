from django.urls import path

from items import ITEMS_ROUTE
from items.graph import graph
from sparql.views import SPARQLQueryAPIView


class ItemsQueryView(SPARQLQueryAPIView):
    """ Query the NLP ontology through SPARQL-Query """

    def graph(self):
        return graph()


ITEMS_URLS = [
    path('{}/query'.format(ITEMS_ROUTE), ItemsQueryView.as_view()),
]
