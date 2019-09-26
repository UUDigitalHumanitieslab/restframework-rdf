"""
Algorithms and manage.py command for migrating RDF data.
"""

from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


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
            graph = import_module('.graph', pkg_name)
            fixture = import_module('.fixture', pkg_name)
            self.migrate_graph(graph.graph, fixture.canonical_graph())
            self.stdout.write('Applied RDF migrations for {}.'.format(pkg_name))
        except ImportError:
            # Nothing to do, this package has no RDF migrations.
            pass
        except AttributeError:
            # Likewise.
            pass

    def migrate_graph(self, actual, desired):
        """ Update the `actual` graph to match `desired`. """
        additions = desired - actual
        deletions = actual - desired
        # TODO: compute subject nodes that weren't in `actual` before.
        # TODO: compute subject nodes that will disappear from `actual`.
        # Do the additions first in case we need to update referencing triples.
        for addition in additions:
            actual.add(addition)
        # TODO: insert post-add logic here
        # TODO: insert pre-delete logic here
        for deletion in deletions:
            actual.remove(deletion)
