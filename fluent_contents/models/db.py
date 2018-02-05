from __future__ import unicode_literals

from copy import deepcopy

import django
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.functional import cached_property
from future.utils import with_metaclass, python_2_unicode_compatible, PY3
from django.contrib.contenttypes.models import ContentType
from django.db import connection, models
from django.db.backends.utils import truncate_name
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from fluent_contents import appsettings
from fluent_contents.cache import get_placeholder_cache_key
from fluent_contents.models.managers import PlaceholderManager, ContentItemManager, get_parent_language_code
from fluent_contents.models.mixins import CachedModelMixin

from parler.models import TranslatableModel
from parler.signals import post_translation_delete
from parler.utils import get_language_title
from polymorphic.base import PolymorphicModelBase

try:
    from polymorphic.models import PolymorphicModel  # django-polymorphic 0.8
except ImportError:
    from polymorphic import PolymorphicModel

# Leave flag so testing this feature is possible.
OPTIMIZE_TRANSLATED_MODEL = True


@python_2_unicode_compatible
class Placeholder(models.Model):
    """
    The placeholder groups various :class:`ContentItem` models together in a single compartment.
    It is the reference point to render custom content.
    Each placeholder is identified by a `slot` name and `parent` object.

    Optionally, the placeholder can have a `title`, and `role`.
    The role is taken into account by the client-side placeholder editor when a page switches template layouts.
    Content items are migrated to the apropriate placeholder, first matched by slot name, secondly matched by role.

    The parent object is stored in a generic relation, so the placeholder can be used with any custom object.
    By adding a :class:`~fluent_contents.models.PlaceholderRelation` field to the parent model, the relation can be traversed backwards.
    From the placeholder, the :attr:`contentitem_set` can be traversed to find the associated :class:`ContentItem` objects.
    Since a :class:`ContentItem` is polymorphic, the actual sub classes of the :class:`ContentItem` will be returned by the query.
    To prevent this behavior, call :func:`~polymorphic.query.PolymorphicQuerySet.non_polymorphic` on the `QuerySet`.
    """
    # The 'role' field is useful for layout switching by a CMS,
    # e.g. moving from a 2-col layout to a 3-col layout.
    # Based on the role of the placeholders, meaningful conversions can be made.
    MAIN = 'm'
    SIDEBAR = 's'
    RELATED = 'r'
    ROLES = (
        (MAIN, _('Main content')),
        (SIDEBAR, _('Sidebar content')),
        (RELATED, _('Related content'))
    )

    slot = models.SlugField(_('Slot'), help_text=_("A short name to identify the placeholder in the template code."))
    role = models.CharField(_('Role'), max_length=1, choices=ROLES, default=MAIN, help_text=_("This defines where the object is used."))

    # Track relation to parent (e.g. page or article)
    parent_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)  # Used to be null for global placeholders, but the 'sharedcontent' plugin solves this issue.
    parent_id = models.IntegerField(null=True)    # Need to allow Null, because Placeholder is created before parent is saved.
    parent = GenericForeignKey('parent_type', 'parent_id')

    title = models.CharField(_('Admin title'), max_length=255, blank=True)

    objects = PlaceholderManager()

    class Meta:
        app_label = 'fluent_contents'  # required for subfolder
        verbose_name = _("Placeholder")
        verbose_name_plural = _("Placeholders")
        unique_together = ('parent_type', 'parent_id', 'slot')

    def __str__(self):
        return self.title or self.slot

    def __repr__(self):
        return '<{0}: {1}; slot: {2}>'.format(self.__class__.__name__, unicode(self), self.slot)

    def get_allowed_plugins(self):
        """
        Return the plugins which are supported in this placeholder.
        """
        from fluent_contents import extensions  # avoid circular import
        return extensions.plugin_pool.get_allowed_plugins(self.slot)

    def get_content_items(self, parent=None, limit_parent_language=True):
        """
        Return all models which are associated with this placeholder.
        Because a :class:`ContentItem` is polymorphic, the actual sub classes of the content item will be returned by the query.

        By passing the :attr:`parent` object, the items can additionally
        be filtered by the parent language.
        """
        # Optimization: if the parent is a TranslatableModel,
        # the code can already tell if there can be any content items.
        # If there is no translation for a current language, avoid trying to fetch items.
        # This speeds up sites where all content exists in fallback languages only.
        if OPTIMIZE_TRANSLATED_MODEL \
        and parent is not None \
        and limit_parent_language \
        and isinstance(parent, TranslatableModel) \
        and not parent.has_translation():
            return ContentItem.objects.none()

        item_qs = self.contentitems.all()   # django-polymorphic FTW!

        if parent:
            # Filtering by parent should return the same results,
            # unless the database is broken by having objects reference the wrong placeholders.
            # Additionally, the `limit_parent_language` argument is supported.
            item_qs = item_qs.parent(parent, limit_parent_language=limit_parent_language)
        else:
            # For accurate rendering filtering by parent is needed.
            # Otherwise, we risk returning stale objects which are indeed attached to this placeholder,
            # but belong to a different parent. This can only happen when manually changing database contents.
            # The admin won't display anything, as it always filters the parent. Hence, do the same for other queries.
            item_qs = item_qs.filter(
                parent_type_id=self.parent_type_id,
                parent_id=self.parent_id
            )

        return item_qs

    def get_search_text(self, fallback_language=None):
        """
        Get the search text for all contents of this placeholder.

        :param fallback_language: The fallback language to use if there are no items in the current language.
                                  Passing ``True`` uses the default :ref:`FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE`.
        :type fallback_language: bool|str
        :rtype: str
        """
        from fluent_contents.rendering import render_placeholder_search_text
        return render_placeholder_search_text(self, fallback_language=fallback_language)

    def get_absolute_url(self):
        """
        Return the URL of the parent object, if it has one.
        This method mainly exists to support cache mechanisms (e.g. refreshing a Varnish cache), and assist in debugging.
        """
        if not self.parent_id or not self.parent_type_id:
            return None

        try:
            return self.parent.get_absolute_url()
        except AttributeError:
            return None

    def delete(self, *args, **kwargs):
        # Some databases may not have a proper ON DELETE rule set, causing a DatabaseError on delete.
        # This happened because South 0.7.4 didn't support on_delete=SET_NULL.
        ContentItem.objects.filter(placeholder=self).update(placeholder=None)
        super(Placeholder, self).delete(*args, **kwargs)

    delete.alters_data = True


class ContentItemMetaClass(PolymorphicModelBase):
    """
    Metaclass for all plugin models.

    Set db_table if it has not been customized.
    """
    # Inspired by from Django-CMS, (c) , BSD licensed.

    def __new__(mcs, name, bases, attrs):
        if django.VERSION < (2, 0):
            # Silence polymorphic messages for wrong manager inheritance,
            # let everything work just like before.
            try:
                attrs['Meta'].manager_inheritance_from_future = True
            except KeyError:
                pass

        new_class = super(ContentItemMetaClass, mcs).__new__(mcs, name, bases, attrs)
        db_table  = new_class._meta.db_table
        app_label = new_class._meta.app_label

        if name != 'ContentItem':
            if db_table.startswith(app_label + '_'):
                model_name = db_table[len(app_label) + 1:]
                new_class._meta.db_table = truncate_name("contentitem_%s_%s" % (app_label, model_name), connection.ops.max_name_length())
                if hasattr(new_class._meta, 'original_attrs'):
                    # Make sure that the Django migrations also pick up this change!
                    # Changing the db_table beforehand might be cleaner,
                    # but also requires duplicating the whole algorithm that Django uses.
                    new_class._meta.original_attrs['db_table'] = new_class._meta.db_table

            # Enforce good manners. The name is often not visible, except for the delete page.
            if not new_class._meta.abstract:
                if not hasattr(new_class, '__str__') or new_class.__str__ == ContentItem.__str__:
                    if PY3:
                        raise TypeError("The {0} class should implement a __str__() function.".format(name))
                    else:
                        # The first check is for python_2_unicode_compatible tricks, also check for __unicode__ only.
                        if not hasattr(new_class, '__unicode__') or new_class.__unicode__ == ContentItem.__unicode__:
                            raise TypeError("The {0} class should implement a __unicode__() or __str__() function.".format(name))

        return new_class


@python_2_unicode_compatible
class ContentItem(with_metaclass(ContentItemMetaClass, CachedModelMixin, PolymorphicModel)):
    """
    A `ContentItem` represents a content part (also called pagelet in other systems) which is displayed in a :class:`Placeholder`.
    To use the `ContentItem`, derive it in your model class:

    .. code-block:: python

        class ExampleItem(ContentItem):
            # any custom fields here

            class Meta:
                verbose_name = "Example item"

    All standard Django model fields can be used in a `ContentItem`. Some things to note:

    * There are special fields for URL, WYSIWYG and file/image fields, which keep the admin styles consistent.
      These are the :class:`~fluent_contents.extensions.PluginFileField`,
      :class:`~fluent_contents.extensions.PluginHtmlField`,
      :class:`~fluent_contents.extensions.PluginImageField` and
      :class:`~fluent_contents.extensions.PluginUrlField` fields.
      See the :ref:`custom-model-fields` section for more details.
    * When adding a M2M field, make sure to override :attr:`copy_to_placeholder`, so the M2M data will be copied.

    When querying the objects through the ORM, the derived instances will be returned automatically.
    This happens because the `ContentItem` class is polymorphic:

    >>> from fluent_contents.models import ContentItem
    >>> ContentItem.objects.all()
    [<ArticleTextItem: Main article>, <RawHtmlItem: test>, <CodeItem: def foo(): print 1>,
    <AnnouncementBlockItem: Test>, <ArticleTextItem: Text in sidebar>]

    Note that the `django-polymorphic` application is written in such way, that this requires the least amount of queries necessary.
    When access to the polymorphic classes is not needed, call :func:`~polymorphic.query.PolymorphicQuerySet.non_polymorphic` on the `QuerySet` to prevent this behavior:

    >>> from fluent_contents.models import ContentItem
    >>> ContentItem.objects.all().non_polymorphic()
    [<ContentItem: Article text item#1 in 'Main content'>, <ContentItem: HTML code#5 in 'Main content'>, <ContentItem: Code snippet#6 in 'Main content'>,
    <ContentItem: Announcement block#7 in 'Main content'>, <ContentItem: Article text item#4 in 'Sidebar'>]

    Being polymorphic also means the base class provides some additional methods such as:

    * :func:`get_real_instance`
    * :func:`get_real_instance_class`

    Each `ContentItem` references both it's parent object (e.g. a page, or article), and the placeholder.
    While this is done mainly for internal reasons, it also provides an easy way to query all content items of a parent.
    The parent object is stored in a generic relation, so the `ContentItem` can be used with any custom object.
    By adding a :class:`~fluent_contents.models.ContentItemRelation` field to the parent model, the relation can be traversed backwards.

    Because the `ContentItem` references it's parent, and not the other way around,
    it will be cleaned up automatically by Django when the parent object is deleted.

    To use a `ContentItem` in the :class:`~fluent_contents.models.PlaceholderField`,
    register it via a plugin definition. see the :class:`~fluent_contents.extensions.ContentPlugin` class for details.

    The rendering of a `ContentItem` class happens in the associate :class:`~fluent_contents.extensions.ContentPlugin` class.
    To render content items outside the template code, use the :mod:`fluent_contents.rendering` module to render the items.
    """

    # When adding objects, the placeholder cache should still be emptied
    clear_cache_on_add = True

    objects = ContentItemManager()

    # Note the validation settings defined here are not reflected automatically
    # in the admin interface because it uses a custom ModelForm to handle these fields.

    # Track relation to parent
    # This makes it much easier to use it as inline.
    parent_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_id = models.IntegerField(null=True)    # Need to allow Null, because Placeholder is created before parent is saved.
    parent = GenericForeignKey('parent_type', 'parent_id')
    language_code = models.CharField(max_length=15, db_index=True, editable=False, default='')

    # Deleting a placeholder should not remove the items, only makes them orphaned.
    # Also, when updating the page, the PlaceholderEditorInline first adds/deletes placeholders before the items are updated.
    placeholder = models.ForeignKey(Placeholder, related_name='contentitems', null=True, on_delete=models.SET_NULL)
    sort_order = models.IntegerField(default=1, db_index=True)

    @cached_property
    def plugin(self):
        """
        Access the parent plugin which renders this model.

        :rtype: :class:`~fluent_contents.extensions.ContentPlugin`
        """
        from fluent_contents.extensions import plugin_pool
        model = self.__class__
        if model is ContentItem:
            # Also allow a non_polymorphic() queryset to resolve the plugin.
            # Corresponding plugin_pool method is still private on purpose.
            # Not sure the utility method should be public, or how it should be named.
            return plugin_pool._get_plugin_by_content_type(self.polymorphic_ctype_id)
        else:
            return plugin_pool.get_plugin_by_model(model)

    def __str__(self):
        # Note this representation is optimized for the admin delete page.
        # Make sure that the
        try:
            real_type = ContentType.objects.get_for_id(self.polymorphic_ctype_id).model_class()
        except ContentType.DoesNotExist:
            real_type_text = "(type deleted)"
        else:
            if real_type is None:
                real_type_text = "(type deleted)"
            else:
                real_type_text = "(type deleted)"

        return u"'{type} {id:d}' in '{language} {placeholder}'".format(
            type=real_type_text,
            id=self.id or 0,
            language=get_language_title(self.language_code) if self.language_code else None,
            placeholder=self.placeholder
        )

    class Meta:
        app_label = 'fluent_contents'  # required for models subfolder
        ordering = ('placeholder', 'sort_order')
        verbose_name = _('Contentitem link')
        verbose_name_plural = _('Contentitem links')

    def get_absolute_url(self):
        """
        Return the URL of the parent object, if it has one.
        This method mainly exists to refreshing cache mechanisms.
        """
        # Allows quick debugging, and cache refreshes.
        parent = self.parent
        try:
            return parent.get_absolute_url()
        except AttributeError:
            return None

    def move_to_placeholder(self, placeholder, sort_order=None):
        """
        .. versionadded: 1.0.2 Move this content item to a new placeholder.

        The object is saved afterwards.
        """
        # Transfer parent
        self.placeholder = placeholder
        self.parent_type = placeholder.parent_type
        self.parent_id = placeholder.parent_id

        try:
            # Copy cache property set by GenericForeignKey (_meta.virtual_fields[0].cache_attr)
            setattr(self, '_parent_cache', placeholder._parent_cache)
        except AttributeError:
            pass

        if sort_order is not None:
            self.sort_order = sort_order
        self.save()

    move_to_placeholder.alters_data = True

    def copy_to_placeholder(self, placeholder, sort_order=None, in_place=False):
        """
        .. versionadded: 1.0 Copy this content item to a new placeholder.

        Note: if you have M2M relations on the model,
        override this method to transfer those values.
        """
        if in_place:
            copy = self
        else:
            copy = deepcopy(self)  # Avoid changing 'self'

        # Reset Django cache
        copy.pk = None  # reset contentitem_ptr_id
        copy.id = None  # reset this base class.
        copy._state.adding = True

        copy.move_to_placeholder(placeholder, sort_order=sort_order)
        return copy

    copy_to_placeholder.alters_data = True

    def save(self, *args, **kwargs):
        # Fallback, make sure the object has a language.
        # As this costs a query per object, the admin formset already sets the language_code whenever it can.
        if not self.language_code:
            self.language_code = get_parent_language_code(self.parent) or appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE

        super(ContentItem, self).save(*args, **kwargs)

    save.alters_data = True

    def get_cache_keys(self):
        """
        Get a list of all cache keys associated with this model.
        This queries the associated plugin for the cache keys it used to store the output at.
        """
        if not self.placeholder_id:
            # TODO: prune old placeholder slot name?
            return []

        # As plugins can change the output caching,
        # they should also return those keys where content is stored at.
        placeholder = self.placeholder
        keys = [
            # Always make sure the base placeholder is cleared,
            # regardless whether get_output_cache_keys() is overwritten.
            get_placeholder_cache_key(placeholder, self.language_code),
        ]
        keys.extend(self.plugin.get_output_cache_keys(placeholder.slot, self))  # ensure list return type.
        return keys


# Instead of overriding the admin classes (effectively inserting the TranslatableAdmin
# in all your PlaceholderAdmin subclasses too), a signal is handled instead.
# It's up to you to decide whether the use the TranslatableAdmin (or any other similar class)
# in your admin for multilingual support. As long as the models provide a get_current_language()
# or `language_code` attribute, the correct contents will be filtered and displayed.
@receiver(post_translation_delete)
def on_delete_model_translation(instance, **kwargs):
    """
    Make sure ContentItems are deleted when a translation in deleted.
    """
    translation = instance

    parent_object = translation.master
    parent_object.set_current_language(translation.language_code)

    # Also delete any associated plugins
    # Placeholders are shared between languages, so these are not affected.
    for item in ContentItem.objects.parent(parent_object, limit_parent_language=True):
        item.delete()  # Delete per item, to trigger cache clearing
