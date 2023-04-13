from sparql.views import SPARQLUpdateAPIView, SPARQLQueryAPIView
from rest_framework.permissions import IsAdminUser
from .graphs import sources_graph, nlp_graph

class QueryView(SPARQLQueryAPIView):
    def graph(self):
        return sources_graph()
    
class UpdateView(SPARQLUpdateAPIView):

    def graph(self):
        return sources_graph()

class NLPQueryView(SPARQLQueryAPIView):
    def graph(self):
        return nlp_graph()