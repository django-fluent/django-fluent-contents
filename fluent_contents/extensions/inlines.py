from django.contrib.admin.options import InlineModelAdmin
from django.db.models.related import RelatedObject
from django.forms.models import BaseInlineFormSet

# The classes here could inherit from NestedFormSetMixin and NestedInlineMixin,
# theirby creating inlines-inline-inlines, but this is not well tested yet.


class BasePluginInlineFormSet(BaseInlineFormSet):

    @classmethod
    def get_default_prefix(cls):
        # Make output less verbose, easier to read, and less kB to transmit.
        # Build the related name on the parent-relation.
        # cls.fk is added by the inlineformset_factory() function.
        rel_name = RelatedObject(cls.fk.rel.to, cls.model, cls.fk).get_accessor_name()
        opts = cls.model._meta
        return '{0}-{1}'.format(opts.object_name.lower(), rel_name.lower())


class PluginInline(InlineModelAdmin):
    """
    The base class for inlines in plugins.
    """
    #template = 'admin/fluent_contents/nested_inlines/{style}.html'
    #style = 'default'
    #formset = BasePluginInlineFormSet
    #extra = 1


class TabularPluginInline(PluginInline):
    template = "admin/fluent_contents/nested_inlines/tabular.html"

class StackedPluginInline(PluginInline):
    template = "admin/fluent_contents/nested_inlines/stacked.html"
