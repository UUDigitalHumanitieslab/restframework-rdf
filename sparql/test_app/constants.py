from rdflib import Namespace

SOURCES_NS = Namespace('{}{}#'.format('http://testserver/', 'source/'))

NLP_ONTOLOGY_NS =  '{}{}#'.format('http://testserver/', 'nlp-ontology')


nlp = Namespace(NLP_ONTOLOGY_NS)
