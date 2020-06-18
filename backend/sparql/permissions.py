from rest_framework.permissions import BasePermission

SPARQL_UPDATE = 'sparql_update'


class SPARQLPermission(BasePermission):
    ''' Custom permission for SPARQL update endpoint.
        Only users in group 'sparql' or admin users are allowed acces.'''

    message = 'Not allowed (no admin or SPARQL-Update permission)'

    def has_permission(self, request, view):
        return request.user.has_perm('rdflib_django.{}'.format(SPARQL_UPDATE))
