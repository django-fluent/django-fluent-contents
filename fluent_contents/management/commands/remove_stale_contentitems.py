from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Model
from fluent_contents.extensions import PluginNotFound
from fluent_contents.models import ContentItem


class Command(BaseCommand):
    help = "Remove ContentItems which are stale, because their model is removed."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-p', '--dry-run', action='store_true', dest='dry_run',
            help="Only list what will change, don't make the actual changes."
        )
        parser.add_argument(
            '-u', '--remove-unreferenced', action='store_true', dest='remove_unreferenced',
            help="Also remove unreferenced items."
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.remove_unreferenced = options['remove_unreferenced']
        #verbosity = options['verbosity']

        stale_cts = self.get_stale_content_types()

        self.remove_stale_items(stale_cts)
        self.remove_unreferenced_items(stale_cts)

    def get_stale_content_types(self):
        stale_cts = {}
        for ct in ContentType.objects.all():
            if ct.model_class() is None:
                stale_cts[ct.pk] = ct
        return stale_cts

    def remove_stale_items(self, stale_cts):
        """
        See if there are items that point to a removed model.
        """
        stale_ct_ids = list(stale_cts.keys())
        items = (ContentItem.objects
                 .non_polymorphic()  # very important, or polymorphic skips them on fetching derived data
                 .filter(polymorphic_ctype__in=stale_ct_ids)
                 .order_by('polymorphic_ctype', 'pk')
                 )
        if not items:
            self.stdout.write("No stale items found.")
            return

        if self.dry_run:
            self.stdout.write("The following content items are stale:")
        else:
            self.stdout.write("The following content items were stale:")

        for item in items:
            ct = stale_cts[item.polymorphic_ctype_id]
            self.stdout.write("- #{id} points to removed {app_label}.{model}".format(
                id=item.pk, app_label=ct.app_label, model=ct.model
            ))

            if not self.dry_run:
                try:
                    item.delete()
                except PluginNotFound:
                    Model.delete(item)

    def remove_unreferenced_items(self, stale_cts):
        """
        See if there are items that no longer point to an existing parent.
        """
        stale_ct_ids = list(stale_cts.keys())
        parent_types = (ContentItem.objects.order_by()
                        .exclude(polymorphic_ctype__in=stale_ct_ids)
                        .values_list('parent_type', flat=True).distinct())

        num_unreferenced = 0

        for ct_id in parent_types:
            parent_ct = ContentType.objects.get_for_id(ct_id)
            unreferenced_items = (ContentItem.objects
                                  .filter(parent_type=ct_id)
                                  .order_by('polymorphic_ctype', 'pk'))

            if parent_ct.model_class() is not None:
                # Only select the items that are part of removed pages,
                # unless the parent type was removed - then removing all is correct.
                unreferenced_items = unreferenced_items.exclude(
                    parent_id__in=parent_ct.get_all_objects_for_this_type()
                )

            if unreferenced_items:
                for item in unreferenced_items:
                    self.stdout.write(
                        "- {cls}#{id} points to nonexisting {app_label}.{model}".format(
                            cls=item.__class__.__name__, id=item.pk,
                            app_label=parent_ct.app_label, model=parent_ct.model
                        ))
                    num_unreferenced += 1
                    if not self.dry_run and self.remove_unreferenced:
                        item.delete()

        if not num_unreferenced:
            self.stdout.write("No unreferenced items found.")
        else:
            self.stdout.write("{0} unreferenced items found.".format(num_unreferenced))
            if not self.remove_unreferenced:
                self.stdout.write("Re-run this command with --remove-unreferenced to remove these items")
