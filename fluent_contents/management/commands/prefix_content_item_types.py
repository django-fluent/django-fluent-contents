from django.core.management.base import BaseCommand
from django.utils.translation import ngettext
from fluent_contents.extensions import plugin_pool
from fluent_contents.management import update_model_prefix


class Command(BaseCommand):
    """
    Add a prefix to the name of content items.
    This makes content items easier to spot in the permissions list.
    """
    help = "Update the names of Content Types of plugins, and insert a prefix.\n" \
           "By default, this happens during syncdb. This commands allows to run the update manually." \
           "It makes content items easier to spot in model lists and the list of permissions."

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        num_updated = 0

        for model in plugin_pool.get_model_classes():
            updated = update_model_prefix(model, verbosity=verbosity)
            if updated:
                num_updated += 1

        self.stdout.write(ngettext(u"{count} item updated.", u"{count} items updated.", num_updated).format(count=num_updated) + u" ")
