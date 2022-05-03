import random
import re

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from items import namespace as ITEM
from rdflib import ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib_django.models import Store

PREFIX_PATTERN = re.compile(r'PREFIX\s+(\w+):\s*<\S+>', re.IGNORECASE)


def get_conjunctive_graph():
    """ Returns the conjunctive graph of our SPARQL store. """
    return ConjunctiveGraph(settings.RDFLIB_STORE)


def prune_triples(graph, triples):
    """Remove all items in iterable `triples` from `graph` (modify in place)."""
    for triple in triples:
        graph.remove(triple)


def prune_triples_cascade(graph, triples, graphs_applied_to=[], privileged_predicates=[]):
    """
    Recursively remove subjects in `triples` and all related resources from `graph`.
    Specify which graphs qualify, i.e. from which triples will be deleted, in `graphs_applied_to`.
    Optionally, skip items related via specific (privileged) predicates.
    """
    for triple in triples:
        prune_recursively(
            graph, triple[0], graphs_applied_to, privileged_predicates
        )


def prune_recursively(graph, subject, graphs_applied_to=[], privileged_predicates=[]):
    """
    Recursively remove subject and all related resources from `graph`.
    Specify which graphs qualify, i.e. from which triples will be deleted, in `graphs_applied_to`.
    Optionally, skip deletion of (i.e. keep) items related via specific (privileged) predicates.
    """
    related_by_subject = list(graph.quads((subject, None, None)))

    for s, p, o, c in related_by_subject:
        if isinstance(o, URIRef) and o != s and p not in privileged_predicates and c in graphs_applied_to:
            prune_recursively(graph, o, graphs_applied_to,
                              privileged_predicates)

    prune_triples(graph, related_by_subject)


def append_triples(graph, triples):
    """ Add all items in iterable `triples` to `graph` (modify in place). """
    for triple in triples:
        graph.add(triple)


def graph_from_triples(triples, ctor=Graph):
    """ Return a new Graph containing all items in iterable `triples`. """
    graph = ctor()
    append_triples(graph, triples)
    return graph


def sample_graph(graph, subjects, request):
    """ Return a random sample from a graph, optionally filtering with a list containing [predicate, object]. """
    n_results = int(request.GET.get('n_results'))
    if len(subjects) > n_results:
        sampled_subjects = random.sample(list(subjects), n_results)
    else:
        sampled_subjects = subjects
    output = Graph()
    for sub in sampled_subjects:
        suggestions = graph.triples((sub, None, None))
        [output.add(s) for s in suggestions]
    return output


def traverse_forward(full_graph, fringe, plys):
    """
    Traverse `full_graph` by object `plys` times, starting from `fringe`.

    Returns a graph with all triples accumulated during the traversal,
    excluding `fringe`.
    """
    result = Graph()
    visited_objects = set()
    while plys > 0:
        objects = set(fringe.objects()) - visited_objects
        if not len(objects):
            break
        fringe = Graph()
        for o in objects:
            if not isinstance(o, Literal):
                append_triples(fringe, full_graph.triples((o, None, None)))
        result |= fringe
        visited_objects |= objects
        plys -= 1
    return result


def traverse_backward(full_graph, fringe, plys):
    """
    Traverse `full_graph` by subject `plys` times, starting from `fringe`.

    Returns a graph with all triples accumulated during the traversal,
    excluding `fringe`. This result always contains complete
    resources, i.e., all triples of each subject in the graph are
    included.
    """
    result = Graph()
    subjects = set(fringe.subjects())
    visited_subjects = set()
    while plys > 0:
        if not len(subjects):
            break
        fringe = Graph()
        fringe_subjects = set()
        for s in subjects:
            parents = set(full_graph.subjects(None, s))
            for ss in parents - fringe_subjects:
                append_triples(fringe, full_graph.triples((ss, None, None)))
            fringe_subjects |= parents
        result |= fringe
        visited_subjects |= subjects
        subjects = set(fringe.subjects()) - visited_subjects
        plys -= 1
    return result


def patched_inject_prefixes(self, query, extra_bindings):
    ''' Monkeypatch for SPARQLStore prefix injection
    Parses the incoming query for prefixes,
    and ignores these when injecting additional namespaces.
    Better implementation is possibly available,
    e.g. use rdfblibs query parser to extract prefixes.
    '''
    query_prefixes = re.findall(PREFIX_PATTERN, query)

    # prefixes available in the query should be deducted from the store's nsBindings
    # prefixes that were provided through initNs should take precedence over all others
    bindings = {x for x in set(self.nsBindings.items())
                if x[0] not in query_prefixes}
    bindings |= set(extra_bindings.items())

    # remove the extra bindings from the original query
    for k in set(extra_bindings.keys()):
        if k in query_prefixes:
            replace_pattern = re.compile(
                fr'PREFIX\s+{k}:\s*<.+>', re.IGNORECASE)
            query = re.sub(replace_pattern, '', query)

    if not bindings:
        return query
    return "\n".join(
        [
            "\n".join(["PREFIX %s: <%s>" % (k, v) for k, v in bindings]),
            "",  # separate ns_bindings from query with an empty line
            query,
        ]
    )


SPARQLStore._inject_prefixes = patched_inject_prefixes
