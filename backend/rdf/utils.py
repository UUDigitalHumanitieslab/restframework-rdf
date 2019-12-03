from rdflib import Graph, Literal


def prune_triples(graph, triples):
    """Remove all items in iterable `triples` from `graph` (modify in place)."""
    for triple in triples:
        graph.remove(triple)


def append_triples(graph, triples):
    """ Add all items in iterable `triples` to `graph` (modify in place). """
    for triple in triples:
        graph.add(triple)


def graph_from_triples(triples):
    """ Return a new Graph containing all items in iterable `triples`. """
    graph = Graph()
    append_triples(graph, triples)
    return graph


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
