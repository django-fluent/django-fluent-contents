from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from fluent_contents.managers import PlaceholderManager, get_parent_lookup_kwargs


class Placeholder(models.Model):
    """
    A placeholder is displayed at a page, rendering custom content.
    """
    # The 'role' field is useful for migrations by a CMS,
    # e.g. moving from a 2-col layout to a 3-col layout.
    # Based on the role of a pageitem, meaningful conversions can be made.
    MAIN = 'm'
    SIDEBAR = 's'
    RELATED = 'r'
    ROLES = (
        (MAIN, _('Main content')),
        (SIDEBAR, _('Sidebar content')),
        (RELATED, _('Related content'))
    )

    slot = models.SlugField(_('Slot'), help_text=_("A short name to identify the placeholder in the template code"))
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
        """
        item_qs = self.contentitems.all()   # django-polymorphic FTW!

        if parent:
            item_qs = item_qs.filter(**get_parent_lookup_kwargs(parent))

        return item_qs


    def get_absolute_url(self):
        # Allows quick debugging, and cache refreshes.
        parent = self.parent
        try:
            return self.parent.get_absolute_url()
        except AttributeError:
            return None




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
            if not hasattr(new_class, '__unicode__'):
                raise FieldError("The {0} class should implement a __unicode__() function.".format(name))

        return new_class


class ContentItem(PolymorphicModel):
    """
    A ```ContentItem``` is a content part which is displayed at a ``Placeholder``.
    The item is rendered by a ``ContentPlugin``.
    """
    __metaclass__ = ContentItemMetaClass

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
    sort_order = models.IntegerField(default=1)


    @property
    def plugin(self):
        """
        Access the parent plugin which renders this model.
        """
        from fluent_contents.extensions import plugin_pool
        return plugin_pool.get_plugin_by_model(self.__class__)


    def __unicode__(self):
        return '<%s#%d, placeholder=%s>' % (self.polymorphic_ctype or self._meta.verbose_name, self.id or 0, self.placeholder)


    class Meta:
        app_label = 'fluent_contents'  # required for models subfolder
        ordering = ('placeholder', 'sort_order')
        verbose_name = _('Contentitem base')
        verbose_name_plural = _('Contentitem bases')


    def get_absolute_url(self):
        # Allows quick debugging, and cache refreshes.
        parent = self.parent
        try:
            return self.parent.get_absolute_url()
        except AttributeError:
            return None
