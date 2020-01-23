""" External namespaces that we use internally. """

from rdflib.namespace import Namespace, RDF, RDFS, OWL, XSD, FOAF, SKOS, DC, DCTERMS

FRBR    = Namespace('http://purl.org/vocab/frbr/core#')
CIDOC   = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
OA      = Namespace('http://www.w3.org/ns/oa#')
AS      = Namespace('http://www.w3.org/ns/activitystreams#')
DCTYPES = Namespace('http://purl.org/dc/dcmitype/')
SCHEMA  = Namespace('http://schema.org/')
HTTP    = Namespace('http://www.w3.org/2011/http#')
HTTPSC  = Namespace('https://www.w3.org/2011/http-statusCodes#')
HTTPM   = Namespace('https://www.w3.org/2011/http-methods#')
ISO6391 = Namespace('http://id.loc.gov/vocabulary/iso639-1/')
OWL     = Namespace('http://www.w3.org/2002/07/owl#')

# URI for representing an unauthenticated visitor, an unknown/multiple languages, or unknown source type.
# Probably not the best possible, but it will do for now.
UNKNOWN = 'https://www.wikidata.org/wiki/Q24238356'
