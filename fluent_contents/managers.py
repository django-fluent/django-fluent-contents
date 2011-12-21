"""
The manager classes are accessed via ``Placeholder.objects``.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType



class PlaceholderManager(models.Manager):
    """
    Extra methods for the placeholder.
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



def get_parent_lookup_kwargs(parent_object):
    """
    Return lookup arguments for the generic ``parent_type`` / ``parent_id`` fields.
    """
    if parent_object is None:
        return dict(
            parent_type__isnull=True,
            parent_id=0
        )
    else:
        return dict(
            parent_type=ContentType.objects.get_for_model(parent_object),
            parent_id=parent_object.pk,
        )
