import re

# These update operations are not supported
# TODO: wiki reference
UPDATE_NOT_SUPPORTED = ['Load', 'Clear',
                        'Drop', 'Add', 'Move', 'Copy', 'Create']
UPDATE_NOT_SUPPORTED_PATTERN = re.compile(
    '|'.join(UPDATE_NOT_SUPPORTED), re.IGNORECASE)
