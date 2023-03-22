from django.urls import path

from nlp_ontology import NLP_ONTOLOGY_ROUTE
from nlp_ontology.graph import graph
from sparql.views import SPARQLQueryAPIView, SPARQLUpdateAPIView


class NlpOntologyQueryView(SPARQLQueryAPIView):

    def graph(self):
        return graph()


class NlpOntologyUpdateView(SPARQLUpdateAPIView):

    def graph(self):
        return graph()


NLP_ONTOLOGY_URLS = [
    path('{}/query'.format(NLP_ONTOLOGY_ROUTE),
         NlpOntologyQueryView.as_view()),
    path('{}/update'.format(NLP_ONTOLOGY_ROUTE),
         NlpOntologyUpdateView.as_view())
]
