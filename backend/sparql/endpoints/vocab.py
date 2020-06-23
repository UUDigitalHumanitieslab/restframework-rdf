from django.urls import path

from vocab import VOCAB_ROUTE
from vocab.graph import graph
from sparql.views import SPARQLQueryAPIView


class VocabQueryView(SPARQLQueryAPIView):
    """ Query the NLP ontology through SPARQL-Query """

    def graph(self):
        return graph()


VOCAB_URLS = [
    path('{}/query'.format(VOCAB_ROUTE), VocabQueryView.as_view()),
]
