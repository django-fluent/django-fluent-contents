import operator
import sys
from functools import reduce

from django.core.management.base import BaseCommand
from django.db import models, ProgrammingError
from django.db.models import Q
from django.utils import six
from django.utils import translation
from django.utils.encoding import force_text
from fluent_contents.extensions import PluginHtmlField, PluginImageField, PluginUrlField
from fluent_contents.extensions import plugin_pool
from html5lib import treebuilders, HTMLParser

try:
    from urllib.parse import unquote  # Python 3
except ImportError:
    from urllib import unquote


def unquote_utf8(value):
    return force_text(unquote(value))


class Command(BaseCommand):
    """
    Add a prefix to the name of content items.
    This makes content items easier to spot in the permissions list.
    """
    help = "Find all link and image URLs in all content items."
    exclude = (
        'KVStore',
        'LogEntry',
        'Session',
    )

    def handle(self, *args, **options):
        translation.activate('en')  # just in case

        self.verbosity = options['verbosity']
        urls = []

        # Look through all registered models.
        for model in sorted(self.get_models(), key=lambda model: model._meta.model_name):
            try:
                urls += self.inspect_model(model)
            except ProgrammingError as e:
                self.stderr.write(force_text(e))

        self.stdout.write("")
        for url in sorted(set(urls)):
            self.stdout.write(url)

    def get_models(self):
        """
        Define which models to include
        """
        # Could also use `apps.get_models()` here.
        return plugin_pool.get_model_classes()

    def inspect_model(self, model):
        """
        Inspect a single model
        """
        # See which interesting fields the model holds.
        url_fields = sorted(f for f in model._meta.fields if isinstance(f, (PluginUrlField, models.URLField)))
        file_fields = sorted(f for f in model._meta.fields if isinstance(f, (PluginImageField, models.FileField)))
        html_fields = sorted(f for f in model._meta.fields if isinstance(f, (models.TextField, PluginHtmlField)))
        all_fields = [f.name for f in (file_fields + html_fields + url_fields)]
        if not all_fields:
            return []

        if model.__name__ in self.exclude:
            self.stderr.write("Skipping {0} ({1})\n".format(model.__name__, ", ".join(all_fields)))
            return []

        sys.stderr.write("Inspecting {0} ({1})\n".format(model.__name__, ", ".join(all_fields)))

        q_notnull = reduce(operator.or_, (Q(**{"{0}__isnull".format(f): False}) for f in all_fields))
        qs = model.objects.filter(q_notnull).order_by('pk')

        urls = []
        for object in qs:
            # HTML fields need proper html5lib parsing
            for field in html_fields:
                value = getattr(object, field.name)
                if value:
                    html_images = self.extract_html_urls(value)
                    urls += html_images

                    for image in html_images:
                        self.show_match(object, image)

            # Picture fields take the URL from the storage class.
            for field in file_fields:
                value = getattr(object, field.name)
                if value:
                    value = unquote_utf8(value.url)
                    urls.append(value)
                    self.show_match(object, value)

            # URL fields can be read directly.
            for field in url_fields:
                value = getattr(object, field.name)
                if value:
                    if isinstance(value, six.text_type):
                        value = force_text(value)
                    else:
                        value = value.to_db_value()  # AnyUrlValue

                    urls.append(value)
                    self.show_match(object, value)
        return urls

    def show_match(self, object, value):
        if self.verbosity >= 2:
            self.stdout.write(u"{0}#{1}: \t{2}".format(object.__class__.__name__, object.pk, value))

    def extract_html_urls(self, html):
        """
        Take all ``<img src="..">`` from the HTML
        """
        p = HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom = p.parse(html)
        urls = []

        for img in dom.getElementsByTagName('img'):
            src = img.getAttribute('src')
            if src:
                urls.append(unquote_utf8(src))

            srcset = img.getAttribute('srcset')
            if srcset:
                urls += self.extract_srcset(srcset)

        for source in dom.getElementsByTagName('source'):
            srcset = source.getAttribute('srcset')
            if srcset:
                urls += self.extract_srcset(srcset)

        for source in dom.getElementsByTagName('a'):
            href = source.getAttribute('href')
            if href:
                urls.append(unquote_utf8(href))

        return urls

    def extract_srcset(self, srcset):
        """
        Handle ``srcset="image.png 1x, image@2x.jpg 2x"``
        """
        urls = []
        for item in srcset.split(','):
            if item:
                urls.append(unquote_utf8(item.rsplit(' ', 1)[0]))
        return urls
