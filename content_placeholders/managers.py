from django.db import models
from django.contrib.contenttypes.models import ContentType



class PlaceholderManager(models.Manager):
    """
    Extra methods for the placeholder
    """

    def parent(self, parent_object):
        """
        Return all placeholders which are associated with a given parent object.
        """
        lookup = _get_lookup_args(parent_object)
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
        parent_attrs = _get_lookup_args(parent_object)
        return self.create(slot=slot, **parent_attrs)



def _get_lookup_args(parent_object):
    return {
        'parent_type': ContentType.objects.get_for_model(parent_object),
        'parent_id': parent_object.pk,
    }
