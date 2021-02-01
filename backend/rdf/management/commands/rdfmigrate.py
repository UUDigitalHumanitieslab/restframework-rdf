"""
Algorithms and manage.py command for migrating RDF data.

Django applications that wish to support this command should include
an rdf_migrations module which should define a Migration class that
derives from rdf.migrations.RDFMigration.
"""

from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from rdf.utils import append_triples, prune_triples, get_conjunctive_graph


class Command(BaseCommand):
    help = 'Performs RDF migrations for the specified app(s).'

    def add_arguments(self, parser):
        parser.add_argument('app_label', nargs='*')

    def handle(self, *args, **options):
        app_labels = options['app_label']
        if len(app_labels) == 0:
            app_labels = settings.INSTALLED_APPS
        else:
            for app in app_labels:
                if app not in settings.INSTALLED_APPS:
                    raise CommandError('{} is not an installed app'.format(app))
        for app in app_labels:
            self.migrate_package(app)

    def migrate_package(self, pkg_name):
        """ Determine whether `pkg` has RDF migrations. If so, apply them. """
        try:
            migrations = import_module('.rdf_migrations', pkg_name)
            self.migrate_graph(migrations.Migration())
            self.stdout.write('Applied RDF migrations for {}.'.format(pkg_name))
        except ImportError:
            # Nothing to do, this package has no RDF migrations.
            pass
        except AttributeError:
            # Likewise.
            pass

    def migrate_graph(self, migration):
        """ Update the `actual` graph to match `desired`. """
        actual = migration.actual()
        desired = migration.desired()
        additions = desired - actual
        deletions = actual - desired
        predicates_present = set(actual.predicates())
        subjects_added = set(additions.subjects())
        subjects_deleted = set(deletions.subjects())
        conjunctive = get_conjunctive_graph()
        # Do the additions first in case we need to update referencing triples.
        append_triples(actual, additions)
        adders = (migration.add_handlers.get(s) for s in subjects_added)
        for handler_name in filter(None, adders):
            getattr(migration, handler_name)(actual, conjunctive)
        deleters = (migration.remove_handlers.get(s) for s in subjects_deleted)
        for handler_name in filter(None, deleters):
            getattr(migration, handler_name)(actual, conjunctive)
        prune_triples(actual, deletions)
        # Handle predicate presence
        presence_handlers = (migration.presence_handlers.get(s)
                             for s in predicates_present)
        for handler_name in filter(None, presence_handlers):
            getattr(migration, handler_name)(actual, conjunctive)
