from rdf.migrations import RDFMigration

from .graph import graph
from .fixture import canonical_graph


class Migration(RDFMigration):
    actual = staticmethod(graph)
    desired = staticmethod(canonical_graph)
