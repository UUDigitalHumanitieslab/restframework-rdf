import re

from django.conf import settings

# These update operations are not supported
# TODO: wiki reference
UPDATE_NOT_SUPPORTED = ['Load', 'Clear',
                        'Drop', 'Add', 'Move', 'Copy', 'Create']
UPDATE_NOT_SUPPORTED_PATTERN = re.compile(
    '|'.join(UPDATE_NOT_SUPPORTED), re.IGNORECASE)

BLANK_NODE_PATTERN = re.compile(r'\[.*\]|_:')

SPARQL_NS = '{}/sparql'.format(settings.RDF_NAMESPACE_ROOT)
