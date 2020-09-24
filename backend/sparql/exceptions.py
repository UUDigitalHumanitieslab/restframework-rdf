from rest_framework.exceptions import APIException, ParseError


class NoParamError(APIException):
    status_code = 400
    default_detail = 'No SPARQL-Query or SPARQL-Update in query or update body parameters.'
    default_code = 'sparql_no_param_error'


class ParseSPARQLError(ParseError):
    default_detail = 'Error parsing SPARQL.'
    default_code = 'sparql_parse_error'


class NotSupportedSPARQLError(ParseError):
    default_detail = 'SPARQL-Update operation not supported.'
    default_code = 'sparql_not_supported'
