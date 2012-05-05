"""
The manager classes are accessed via ``Placeholder.objects``.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from polymorphic import PolymorphicManager, PolymorphicQuerySet



class PlaceholderManager(models.Manager):
    """
    Extra methods for the ``Placeholder.objects``.
    """

    def parent(self, parent_object):
        """
        Return all placeholders which are associated with a given parent object.
        """
        lookup = get_parent_lookup_kwargs(parent_object)
        return self.get_query_set().filter(**lookup)


    def get_by_slot(self, parent_object, slot):
        """
        Return a placeholder by key.
        """
        return self.parent(parent_object).get(slot=slot)


    def create_for_object(self, parent_object, slot):
        """
        Create a placeholder with the given parameters
        """
        parent_attrs = get_parent_lookup_kwargs(parent_object)
        return self.create(slot=slot, **parent_attrs)


class ContentItemQuerySet(PolymorphicQuerySet):
    pass


class ContentItemManager(PolymorphicManager):
    """
    Extra methods for ``ContentItem.objects``.
    """
    def __init__(self, *args, **kwargs):
        super(ContentItemManager, self).__init__(queryset_class=ContentItemQuerySet, *args, **kwargs)


    def parent(self, parent_object):
        """
        Return all content items which are associated with a given parent object.
        """
        lookup = get_parent_lookup_kwargs(parent_object)
        return self.get_query_set().filter(**lookup)


def get_parent_lookup_kwargs(parent_object):
    """
    Return lookup arguments for the generic ``parent_type`` / ``parent_id`` fields.
    """
    if parent_object is None:
        return dict(
            parent_type__isnull=True,
            parent_id=0
        )
    elif isinstance(parent_object, models.Model):
        return dict(
            parent_type=ContentType.objects.get_for_model(parent_object),
            parent_id=parent_object.pk,
        )
    else:
        raise ValueError("parent_object is not a model!")
