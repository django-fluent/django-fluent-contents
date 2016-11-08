from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Model
from fluent_contents.extensions import PluginNotFound
from fluent_contents.models import ContentItem


class Command(BaseCommand):
    help = "Remove ContentItems which are stale, because their model is removed."

    if getattr(BaseCommand, 'add_arguments', None):  # Django 1.8+
        def add_arguments(self, parser):
            super(Command, self).add_arguments(parser)
            parser.add_argument(
                '-p', '--dry-run', action='store_true', dest='dry_run',
                help="Only list what will change, don't make the actual changes."
            )
    else:
        from optparse import make_option
        option_list = BaseCommand.option_list + (
            make_option(
                '-p', '--dry-run', action='store_true', dest='dry_run', default=False,
                help="Only list what will change, don't make the actual changes."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        #verbosity = options['verbosity']

        stale_cts = {}
        for ct in ContentType.objects.all():
            if ct.model_class() is None:
                stale_cts[ct.pk] = ct

        items = (ContentItem.objects
                 .non_polymorphic()  # very important, or polymorphic skips them on fetching derived data
                 .filter(polymorphic_ctype__in=list(stale_cts.keys()))
                 .order_by('polymorphic_ctype', 'pk')
                 )
        if not items:
            self.stdout.write("No stale items found.")
            return

        if dry_run:
            self.stdout.write("The following content items are stale:")
        else:
            self.stdout.write("The following content items were stale:")

        for item in items:
            ct = stale_cts[item.polymorphic_ctype_id]
            self.stdout.write("- #{id} points to removed {app_label}.{model}".format(id=item.pk, app_label=ct.app_label, model=ct.model))
            if not dry_run:
                try:
                    item.delete()
                except PluginNotFound:
                    Model.delete(item)
