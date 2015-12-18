"""
The manager classes are accessed via ``Placeholder.objects``.
"""
import six

from future.builtins import str
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language
from parler.utils import get_language_title
from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


class PlaceholderManager(models.Manager):
    """
    Extra methods for the ``Placeholder.objects``.
    """

    def parent(self, parent_object):
        """
        Return all placeholders which are associated with a given parent object.
        """
        # NOTE: by using .all(), the correct get_queryset() or get_query_set() method is called.
        # Just calling self.get_queryset() will break the RelatedManager.get_query_set() override in Django 1.5
        # This avoids all issues with Django 1.5/1.6/1.7 compatibility.
        lookup = get_parent_lookup_kwargs(parent_object)
        return self.all().filter(**lookup)

    def get_by_slot(self, parent_object, slot):
        """
        Return a placeholder by key.
        """
        placeholder = self.parent(parent_object).get(slot=slot)
        placeholder.parent = parent_object  # fill the reverse cache
        return placeholder

    def create_for_object(self, parent_object, slot, role='m', title=None):
        """
        Create a placeholder with the given parameters
        """
        from .db import Placeholder
        parent_attrs = get_parent_lookup_kwargs(parent_object)
        obj = self.create(
            slot=slot,
            role=role or Placeholder.MAIN,
            title=title or slot.title().replace('_', ' '),
            **parent_attrs
        )
        obj.parent = parent_object  # fill the reverse cache
        return obj


class ContentItemQuerySet(PolymorphicQuerySet):
    """
    QuerySet methods for ``ContentItem.objects.``.
    """

    def translated(self, *language_codes):
        """
        .. versionadded:: 1.0

        Only return translated objects which of the given languages.

        When no language codes are given, only the currently active language is returned.
        """
        # this API has the same semantics as django-parler's .translated() for familiarity.
        # However, since this package doesn't filter in a related field, the ORM limitations don't apply.
        if not language_codes:
            language_codes = (get_language(),)
        else:
            # Since some code operates on a True/str switch, make sure that doesn't drip into this low level code.
            for language_code in language_codes:
                if not isinstance(language_code, six.string_types) or language_code.lower() in ('1', '0', 'true', 'false'):
                    raise ValueError("ContentItemQuerySet.translated() expected language_code to be an ISO code")

        if len(language_codes) == 1:
            return self.filter(language_code=language_codes[0])
        else:
            return self.filter(language_code__in=language_codes)

    def parent(self, parent_object, limit_parent_language=True):
        """
        Return all content items which are associated with a given parent object.
        """
        lookup = get_parent_lookup_kwargs(parent_object)

        # Filter the items by default, giving the expected "objects for this parent" items
        # when the parent already holds the language state.
        if limit_parent_language:
            language_code = get_parent_language_code(parent_object)
            if language_code:
                lookup['language_code'] = language_code

        return self.filter(**lookup)

    def clear_cache(self):
        """
        .. versionadded:: 1.0 Clear the cache of the selected entries.

        This method is not available on the manager class, only the queryset
        (similar to the :func:`~django.db.models.query.QuerySet.delete` method).
        """
        for contentitem in self:
            contentitem.clear_cache()

    clear_cache.alters_data = True

    def move_to_placeholder(self, placeholder, sort_order=None):
        """
        .. versionadded: 1.0.2 Move the entire queryset to a new object.

        Returns a queryset with the newly created objects.
        """
        qs = self.all()  # Get clone
        for item in qs:
            # Change the item directly in the resultset.
            item.move_to_placeholder(placeholder, sort_order=sort_order)
            if sort_order is not None:
                sort_order += 1

        return qs

    move_to_placeholder.alters_data = True

    def copy_to_placeholder(self, placeholder, sort_order=None):
        """
        .. versionadded: 1.0 Copy the entire queryset to a new object.

        Returns a queryset with the newly created objects.
        """
        qs = self.all()  # Get clone
        for item in qs:
            # Change the item directly in the resultset.
            item.copy_to_placeholder(placeholder, sort_order=sort_order, in_place=True)
            if sort_order is not None:
                sort_order += 1

        return qs

    copy_to_placeholder.alters_data = True


class ContentItemManager(PolymorphicManager):
    """
    Extra methods for ``ContentItem.objects``.
    """
    queryset_class = ContentItemQuerySet

    def translated(self, *language_codes):
        """
        .. versionadded:: 1.0

        Only return translated objects which of the given languages.

        When no language codes are given, only the currently active language is returned.
        """
        # NOTE: by using .all(), the correct get_queryset() or get_query_set() method is called.
        # Just calling self.get_queryset() will break the RelatedManager.get_query_set() override in Django 1.5
        # This avoids all issues with Django 1.5/1.6/1.7 compatibility.
        return self.all().translated(language_codes)

    def parent(self, parent_object, limit_parent_language=True):
        """
        Return all content items which are associated with a given parent object.
        """
        return self.all().parent(parent_object, limit_parent_language)

    def create_for_placeholder(self, placeholder, sort_order=1, language_code=None, **kwargs):
        """
        Create a Content Item with the given parameters

        If the language_code is not provided, the language code of the parent will be used.
        This may perform an additional database query, unless
        the :class:`~fluent_contents.models.managers.PlaceholderManager` methods were used to construct the object,
        such as :func:`~fluent_contents.models.managers.PlaceholderManager.create_for_object`
        or :func:`~fluent_contents.models.managers.PlaceholderManager.get_by_slot`
        """
        if language_code is None:
            # Could also use get_language() or appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE
            # thus avoid the risk of performing an extra query here to the parent.
            # However, this identical behavior to BaseContentItemFormSet,
            # and the parent can be set already via Placeholder.objects.create_for_object()
            language_code = get_parent_language_code(placeholder.parent)

        obj = self.create(
            placeholder=placeholder,
            parent_type_id=placeholder.parent_type_id,
            parent_id=placeholder.parent_id,
            sort_order=sort_order,
            language_code=language_code,
            **kwargs
        )

        # Fill the reverse caches
        obj.placeholder = placeholder
        parent = getattr(placeholder, '_parent_cache', None)  # by GenericForeignKey (_meta.virtual_fields[0].cache_attr)
        if parent is not None:
            obj.parent = parent

        return obj


# This low-level function is used for both ContentItem and Placeholder objects.
# Only the first has language_code support, the second one not.
def get_parent_lookup_kwargs(parent_object):
    """
    Return lookup arguments for the generic ``parent_type`` / ``parent_id`` fields.

    :param parent_object: The parent object.
    :type parent_object: :class:`~django.db.models.Model`
    """
    if parent_object is None:
        return dict(
            parent_type__isnull=True,
            parent_id=0
        )
    elif isinstance(parent_object, models.Model):
        return dict(
            parent_type=ContentType.objects.get_for_model(parent_object),
            parent_id=parent_object.pk
        )
    else:
        raise ValueError("parent_object is not a model!")


def get_parent_language_code(parent_object):
    """
    .. versionadded:: 1.0

    Return the parent object language code.

    Tries to access ``get_current_language()`` and ``language_code`` attributes on the parent object.
    """
    if parent_object is None:
        return None

    try:
        # django-parler uses this attribute
        return parent_object.get_current_language()
    except AttributeError:
        pass

    try:
        # E.g. ContentItem.language_code
        return parent_object.language_code
    except AttributeError:
        pass

    return None


def get_parent_active_language_choices(parent_object, exclude_current=False):
    """
    .. versionadded:: 1.0

    Get the currently active languages of an parent object.

    Note: if there is no content at the page, the language won't be returned.
    """
    assert parent_object is not None, "Missing parent_object!"

    from .db import ContentItem
    qs = ContentItem.objects \
        .parent(parent_object, limit_parent_language=False) \
        .values_list('language_code', flat=True).distinct()

    languages = set(qs)

    if exclude_current:
        parent_lang = get_parent_language_code(parent_object)
        try:
            languages.remove(parent_lang)
        except KeyError:
            pass

    # No multithreading issue here, object is instantiated for this user only.
    choices = [(lang, str(get_language_title(lang))) for lang in languages if lang]
    choices.sort(key=lambda tup: tup[1])
    return choices
