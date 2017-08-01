from __future__ import unicode_literals
from future.utils import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from fluent_contents.forms import ContentItemForm
from fluent_contents.models import ContentItem, ContentItemManager
from fluent_contents.plugins.markup import appsettings, backend

LANGUAGE_MODEL_CLASSES = {}

__all__ = [
    'LANGUAGE_MODEL_CLASSES',
]


class MarkupItemForm(ContentItemForm):
    """
    A custom form that validates the markup.
    """
    default_language = None

    def clean_text(self):
        try:
            backend.render_text(self.cleaned_data['text'], self.instance.language or self.default_language)
        except Exception as e:
            raise ValidationError("There is an error in the markup: %s" % e)
        return self.cleaned_data['text']


@python_2_unicode_compatible
class MarkupItem(ContentItem):
    """
    A snippet of markup (restructuredtext, markdown, or textile) to display at a page.
    """
    text = models.TextField(_('markup'))

    # Store the language to keep rendering intact while switching settings.
    language = models.CharField(_('Language'), max_length=30, editable=False, db_index=True, choices=backend.LANGUAGE_CHOICES)

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _('Markup code')
        verbose_name_plural = _('Markup code')

    def __str__(self):
        return Truncator(self.text).words(20)

    def __init__(self, *args, **kwargs):
        super(MarkupItem, self).__init__(*args, **kwargs)

        # Extra polymorphic, in case the base class content ID was stored.
        ProxyModelClass = LANGUAGE_MODEL_CLASSES.get(self.language, None)
        if ProxyModelClass:
            self.__class__ = ProxyModelClass


class MarkupLanguageManager(ContentItemManager):

    def __init__(self, fixed_language):
        super(MarkupLanguageManager, self).__init__()
        self.fixed_language = fixed_language

    def get_queryset(self):
        return super(MarkupLanguageManager, self).get_queryset().filter(language=self.fixed_language)


def _create_markup_model(fixed_language):
    """
    Create a new MarkupItem model that saves itself in a single language.
    """
    title = backend.LANGUAGE_NAMES.get(fixed_language) or fixed_language

    objects = MarkupLanguageManager(fixed_language)

    def save(self, *args, **kwargs):
        self.language = fixed_language
        MarkupItem.save(self, *args, **kwargs)

    class Meta:
        verbose_name = title
        verbose_name_plural = _('%s items') % title
        proxy = True

    classname = "{0}MarkupItem".format(fixed_language.capitalize())

    new_class = type(str(classname), (MarkupItem,), {
        '__module__': MarkupItem.__module__,
        'objects': objects,
        'save': save,
        'Meta': Meta,
    })

    # Make easily browsable
    return new_class


# Create proxy models for all supported languages. This allows reusage of the same database table.
# It does not impact the frontend, as django-polymorphic requests the MarkupItem base class (which is then upcasted in __init__()).
# the admin interface will query the database per language, as it has an inline per plugin type.
for language in list(backend.SUPPORTED_LANGUAGES.keys()):
    if language not in appsettings.FLUENT_MARKUP_LANGUAGES:
        continue

    LANGUAGE_MODEL_CLASSES[language] = _create_markup_model(language)
    #globals()[new_class.__name__] = new_class
    #__all__.append(new_class.__name__)
