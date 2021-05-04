import sys
import re
from rdflib import Literal
from rdf.ns import XSD

# via http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
ILLEGAL_UNICHRS = [
    (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
    (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
    (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
    (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
    (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
    (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
    (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
    (0x10FFFE, 0x10FFFF)
]
ILLEGAL_RANGES = ["%s-%s" % (chr(low), chr(high))
                  for (low, high) in ILLEGAL_UNICHRS if low < sys.maxunicode]

ILLEGAL_XML_RE = re.compile(u'[%s]' % u''.join(ILLEGAL_RANGES))

CLEANABLE_DATATYPES = (None, XSD.string, XSD.normalizedString)


def invalid_xml_remove(c):
    return re.sub(ILLEGAL_XML_RE, ' ', c)


def find_invalid_xml(c):
    return re.search(ILLEGAL_XML_RE, c)


def is_cleanable(term):
    return isinstance(term, Literal) and term.datatype in CLEANABLE_DATATYPES


def clean_term(term):
    if not is_cleanable(term):
        return term
    return Literal(invalid_xml_remove(term.value),
                   lang=term.language,
                   datatype=term.datatype)


def xml_sanitize_triple(triple):
    if any((is_cleanable(term)) for term in triple):
        cleaned_triple = tuple([clean_term(t) for t in triple])
        if cleaned_triple != triple:
            return (True, cleaned_triple)
    return (False, triple)
