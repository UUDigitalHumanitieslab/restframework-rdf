from django.db import models, DatabaseError
from django.db.transaction import atomic
# See https://docs.djangoproject.com/en/2.2/_modules/django/utils/decorators/
from django.utils.decorators import classproperty


class BaseCounter(models.Model):
    class Meta:
        abstract = True

    """ AUTOINCREMENT for RDF subject URIs. """
    count = models.PositiveIntegerField()

    @property
    def namespace(self):
        raise NotImplementedError()

    @classproperty
    def current(cls):
        """ Get or create a singleton instance of ItemCounter. """
        instance = cls.objects.all().first()
        if not instance:
            instance = cls(count=1)
            instance.save()
        return instance

    def __str__(self):
        """ The subject URI associated with the current value of `count`. """
        return '{}{}'.format(self.namespace, self.count)

    def increment(self):
        """ Add 1 to the count and save immediately. """
        decrement_on_rollback = False
        try:
            with atomic():
                if self.pk:
                    self.refresh_from_db()
                self.count += 1
                decrement_on_rollback = True
                self.save()
        except DatabaseError:
            if decrement_on_rollback:
                self.count -= 1
            raise
