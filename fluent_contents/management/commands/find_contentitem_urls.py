import operator
from functools import reduce

import sys
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils import six
from fluent_contents.extensions import PluginHtmlField, PluginImageField, PluginUrlField
from fluent_contents.extensions import plugin_pool
from html5lib import treebuilders, HTMLParser


class Command(BaseCommand):
    """
    Add a prefix to the name of content items.
    This makes content items easier to spot in the permissions list.
    """
    help = "Find all link and image URLs in all content items."

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        urls = []

        # Look through all registered models.
        for model in plugin_pool.get_model_classes():
            urls += self.inspect_model(model)

        self.stdout.write("")
        for urls in sorted(set(urls)):
            self.stdout.write(urls)

    def inspect_model(self, model):
        """
        Inspect a single model
        """
        # See which interesting fields the model holds.
        url_fields = sorted(f for f in model._meta.fields if isinstance(f, (PluginUrlField, models.URLField)))
        picture_fields = sorted(f for f in model._meta.fields if isinstance(f, (PluginImageField, models.ImageField)))
        html_fields = sorted(f for f in model._meta.fields if isinstance(f, PluginHtmlField))
        if not picture_fields and not html_fields and not url_fields:
            return []

        all_fields = [f.name for f in (picture_fields + html_fields + url_fields)]
        sys.stderr.write("Inspecting {0} ({1})\n".format(model.__name__, ", ".join(all_fields)))

        q_notnull = reduce(operator.or_, (Q(**{"{0}__isnull".format(f): False}) for f in all_fields))
        qs = model.objects.filter(q_notnull).order_by('pk')

        urls = []
        for contentitem in qs:
            # HTML fields need proper html5lib parsing
            for field in html_fields:
                value = getattr(contentitem, field.name)
                if value:
                    html_images = self.extract_html_urls(value)

                    for image in html_images:
                        self.show_match(contentitem, image)
                    urls += html_images

            # Picture fields take the URL from the storage class.
            for field in picture_fields:
                value = getattr(contentitem, field.name)
                if value:
                    self.show_match(contentitem, value)
                    urls.append(force_text(value.url))

            # URL fields can be read directly.
            for field in url_fields:
                value = getattr(contentitem, field.name)
                if isinstance(value, six.text_type):
                    urls.append(value)
                else:
                    urls.append(value.to_db_value())  # AnyUrlValue
        return urls

    def show_match(self, contentitem, value):
        if self.verbosity >= 2:
            self.stdout.write("{0}#{1}: \t{2}".format(contentitem.__class__.__name__, contentitem.pk, value))

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
                urls.append(src)

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
                urls.append(href)

        return urls

    def extract_srcset(self, srcset):
        """
        Handle ``srcset="image.png 1x, image@2x.jpg 2x"``
        """
        urls = []
        for item in srcset.split(','):
            if item:
                urls.append(item.rsplit(' ', 1)[0])
        return urls
