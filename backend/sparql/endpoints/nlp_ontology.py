from django.urls import path

from nlp_ontology import NLP_ONTOLOGY_ROUTE
from nlp_ontology.graph import graph
from sparql.views import SPARQLQueryAPIView, SPARQLUpdateAPIView


class NlpOntologyQueryView(SPARQLQueryAPIView):
    """ Query the NLP ontology through SPARQL-Query """

    def graph(self):
        return graph()


class NlpOntologyUpdateView(SPARQLUpdateAPIView):
    """ Update the NLP ontology through SPARQL-Update """

    def graph(self):
        return graph()


NLP_ONTOLOGY_URLS = [
    path('{}/query'.format(NLP_ONTOLOGY_ROUTE),
         NlpOntologyQueryView.as_view()),
    path('{}/update'.format(NLP_ONTOLOGY_ROUTE),
         NlpOntologyUpdateView.as_view())
]
