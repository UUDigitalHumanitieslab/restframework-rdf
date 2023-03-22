from django.urls import path

from ontology import ONTOLOGY_ROUTE
from ontology.graph import graph
from sparql.views import SPARQLQueryAPIView


class OntologyQueryView(SPARQLQueryAPIView):

    def graph(self):
        return graph()


ONTOLOGY_URLS = [
    path('{}/query'.format(ONTOLOGY_ROUTE), OntologyQueryView.as_view()),
]
