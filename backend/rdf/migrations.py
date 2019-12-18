from rdflib import URIRef

MIGRATION_OVERRIDE_MESSAGE = 'Override this method to return an rdflib.Graph.'


def on_add(uri):
    """
    Decorator for RDFMigration class methods.

    Use this to mark a method as handling the introduction of a
    particular subject URI. Each method can be decorated only once in
    this way, although it is possible to mark a method as handling
    both an addition and a removal. Conversely, each URI can be
    handled by only one method, although both its addition and its
    removal can be handled.
    """
    def decorator(method):
        method.__handles_addition__ = URIRef(uri)
        return method
    return decorator


def on_remove(uri):
    """
    Decorator for RDFMigration class methods.

    Use this to mark a method as handling the removal of a particular
    subject URI. Each method can be decorated only once in this way,
    although it is possible to mark a method as handling both an
    addition and a removal. Conversely, each URI can be handled by
    only one method, although both its addition and its removal can
    be handled.
    """
    def decorator(method):
        method.__handles_removal__ = URIRef(uri)
        return method
    return decorator


class MetaRDFMigration(type):
    """
    Metaclass that ensures the presence of .add_handlers et al.

    This should be considered an implementation detail of RDFMigration.
    """

    def __new__(cls, name, bases, namespace, **kwargs):
        augmented = super().__new__(cls, name, bases, namespace, **kwargs)
        add_handlers = {}
        del_handlers = {}
        for attribute_name, value in augmented.__dict__.items():
            add_uri = getattr(value, '__handles_addition__', None)
            del_uri = getattr(value, '__handles_removal__', None)
            if add_uri:
                add_handlers[add_uri] = attribute_name
            if del_uri:
                del_handlers[del_uri] = attribute_name
        augmented.add_handlers = add_handlers
        augmented.remove_handlers = del_handlers
        return augmented


class RDFMigration(metaclass=MetaRDFMigration):
    """
    Base class for RDF migrations.

    At a minimum, every derived class should override the .actual and
    .desired member functions, both of which must return an
    rdflib.Graph. If you are assigning free functions to these
    members, for example imported from another module, make sure to
    wrap them with staticmethod().

    By default, .actual() will be updated to match .desired()
    exactly. If you need to do extra work, define additional methods
    that are decorated with @on_add or @on_remove (documented above).
    These methods should take three arguments, `self`, `actual` and
    `conjunctive`, where `actual` is the result of `self.actual()`
    and `conjunctive` is the full conjunctive graph from the Django
    store. The return value is ignored; migration methods should take
    effect by directly modifying either `actual` or `conjunctive`.

    Migrations are executed in the following order:

      1. Add new triples from the desired graph to the actual graph.
      2. Execute addition handler methods (relative order undefined).
      3. Execute removal handler methods (relative order undefined).
      4. Remove triples from the actual that disappeared in the desired.

    A migration class is instantiated before application, so in
    principle, you can make a migration stateful. However, keep in
    mind that the relative order of addition handlers and removal
    handlers is undefined; for this reason, it is safer to keep the
    migration stateless if possible.

    If you define an __init__ method, give it a (self, *args, **kwargs)
    signature in order to make it forward-compatible. Currently, no
    arguments are passed, but this might change in the future.
    """

    def actual(self):
        raise NotImplementedError(MIGRATION_OVERRIDE_MESSAGE)

    def desired(self):
        raise NotImplementedError(MIGRATION_OVERRIDE_MESSAGE)
