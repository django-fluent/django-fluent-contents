from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import FieldError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from fluent_contents.cache import get_rendering_cache_key
from fluent_contents.models.managers import PlaceholderManager, ContentItemManager, get_parent_lookup_kwargs


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
    parent_type = models.ForeignKey(ContentType, null=True, blank=True)  # Allow null for global placeholders
    parent_id = models.IntegerField(null=True)    # Need to allow Null, because Placeholder is created before parent is saved.
    parent = GenericForeignKey('parent_type', 'parent_id')

    title = models.CharField(_('Admin title'), max_length=255, blank=True)

    objects = PlaceholderManager()

    class Meta:
        app_label = 'fluent_contents'  # required for subfolder
        verbose_name = _("Placeholder")
        verbose_name_plural = _("Placeholders")
        unique_together = ('parent_type', 'parent_id', 'slot')

    def __unicode__(self):
        return self.title or self.slot


    def get_allowed_plugins(self):
        """
        Return the plugins which are supported in this placeholder.
        """
        from fluent_contents import extensions  # avoid circular import
        return extensions.plugin_pool.get_plugins()


    def get_content_items(self, parent=None):
        """
        Return all models which are associated with this placeholder.
        Because a :class:`ContentItem` is polymorphic, the actual sub classes of the content item will be returned by the query.
        """
        item_qs = self.contentitems.all()   # django-polymorphic FTW!

        if parent:
            item_qs = item_qs.filter(**get_parent_lookup_kwargs(parent))

        return item_qs


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

    def delete(self, using=None):
        # Workaround for the fact that South 0.7.4 does not support on_delete=SET_NULL yet
        # It doesn't add that attribute to the foreign key, causing a DatabaseError instead.
        ContentItem.objects.filter(placeholder=self).update(placeholder=None)
        super(Placeholder, self).delete(using)



class ContentItemMetaClass(PolymorphicModelBase):
    """
    Metaclass for all plugin models.

    Set db_table if it has not been customized.
    """
    # Inspired by from Django-CMS, (c) , BSD licensed.

    def __new__(mcs, name, bases, attrs):
        new_class = super(ContentItemMetaClass, mcs).__new__(mcs, name, bases, attrs)
        db_table  = new_class._meta.db_table
        app_label = new_class._meta.app_label

        if name != 'ContentItem':
            if db_table.startswith(app_label + '_'):
                model_name = db_table[len(app_label)+1:]
                new_class._meta.db_table = "contentitem_%s_%s" % (app_label, model_name)

            # Enforce good manners. The name is often not visible, except for the delete page.
            if not hasattr(new_class, '__unicode__') or new_class.__unicode__ == ContentItem.__unicode__:
                raise FieldError("The {0} class should implement a __unicode__() function.".format(name))

        return new_class


class ContentItem(PolymorphicModel):
    """
    A `ContentItem` represents a content part (also called pagelet in other systems) which is displayed in a :class:`Placeholder`.
    To use the `ContentItem`, derive it in your model class:

    .. code-block:: python

        class ExampleItem(ContentItem):
            # any custom fields here

            class Meta:
                verbose_name = "Example item"

    The `ContentItem` class is polymorphic; when querying the objects, the derived instances will be returned automatically:

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
    __metaclass__ = ContentItemMetaClass
    objects = ContentItemManager()

    # Note the validation settings defined here are not reflected automatically
    # in the admin interface because it uses a custom ModelForm to handle these fields.

    # Track relation to parent
    # This makes it much easier to use it as inline.
    parent_type = models.ForeignKey(ContentType)
    parent_id = models.IntegerField(null=True)    # Need to allow Null, because Placeholder is created before parent is saved.
    parent = GenericForeignKey('parent_type', 'parent_id')

    # Deleting a placeholder should not remove the items, only makes them orphaned.
    # Also, when updating the page, the PlaceholderEditorInline first adds/deletes placeholders before the items are updated.
    placeholder = models.ForeignKey(Placeholder, related_name='contentitems', null=True, on_delete=models.SET_NULL)
    sort_order = models.IntegerField(default=1, db_index=True)


    @property
    def plugin(self):
        """
        Access the parent plugin which renders this model.

        :rtype: :class:`~fluent_contents.extensions.ContentPlugin`
        """
        from fluent_contents.extensions import plugin_pool
        if self.__class__ in (ContentItem,):
            # Also allow a non_polymorphic() queryset to resolve the plugin.
            # Corresponding plugin_pool method is still private on purpose.
            # Not sure the utility method should be public, or how it should be named.
            return plugin_pool._get_plugin_by_content_type(self.polymorphic_ctype_id)
        else:
            return plugin_pool.get_plugin_by_model(self.__class__)


    def __unicode__(self):
        return u"{type} {id:d} in '{placeholder}'".format(
            type=self.polymorphic_ctype or self._meta.verbose_name,
            id=self.id or 0,
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
            return self.parent.get_absolute_url()
        except AttributeError:
            return None

    def save(self, *args, **kwargs):
        super(ContentItem, self).save(*args, **kwargs)
        self.clear_cache()


    def delete(self, *args, **kwargs):
        super(ContentItem, self).delete(*args, **kwargs)
        self.clear_cache()


    def clear_cache(self):
        """
        Delete the cache keys associated with this model.
        """
        for cache_key in self.get_cache_keys():
            cache.delete(cache_key)


    def get_cache_keys(self):
        """
        Get a list of all cache keys associated with this model.
        """
        if not self.placeholder_id:
            # TODO: prune old placeholder slot name?
            return []

        placeholder_name = self.placeholder.slot
        return [
            get_rendering_cache_key(placeholder_name, self)
        ]
