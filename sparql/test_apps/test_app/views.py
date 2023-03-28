from sparql.views import SPARQLUpdateAPIView, SPARQLQueryAPIView
from rest_framework.permissions import IsAdminUser
from .graph import graph

class QueryView(SPARQLQueryAPIView):
    def graph(self):
        return graph()
    
class UpdateView(SPARQLUpdateAPIView):
    permission_classes = [IsAdminUser]

    def graph(self):
        return graph()