from django.urls import path

from items import ITEMS_SLUG
from items.graph import graph
from sparql.views import SPARQLQueryAPIView, SPARQLUpdateAPIView


class ItemsQueryView(SPARQLQueryAPIView):

    def graph(self):
        return graph()


class ItemsUpdateView(SPARQLUpdateAPIView):

    def graph(self):
        return graph()


ITEMS_URLS = [
    path('{}/query'.format(ITEMS_SLUG), ItemsQueryView.as_view()),
    path('{}/update'.format(ITEMS_SLUG), ItemsUpdateView.as_view())
]
