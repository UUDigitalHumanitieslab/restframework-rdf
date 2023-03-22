from rest_framework.urlpatterns import format_suffix_patterns

from .endpoints import SPARQL_URLS

urlpatterns = format_suffix_patterns(SPARQL_URLS)
