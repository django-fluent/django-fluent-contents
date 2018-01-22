import fluent_contents
import os, re
from importlib import import_module

from django.core.management import CommandError
from django.core.management.templates import TemplateCommand

RE_PLUGIN = re.compile('Plugin$')


class Command(TemplateCommand):
    """
    Add a prefix to the name of content items.
    This makes content items easier to spot in the permissions list.
    """
    help = (
        "Creates a Django app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--plugin', '-p', dest='plugin',
            help='The name of the ContentPlugin subclass to render.'
        )
        parser.add_argument(
            '--model', '-m', dest='model',
            help='The name of the ContentItem model subclass to render.'
        )

    def handle(self, *args, **options):
        app_name, target = options.pop('name'), options.pop('directory')
        self.validate_name(app_name, "app")

        # Check that the app_name cannot be imported.
        try:
            import_module(app_name)
        except ImportError:
            pass
        else:
            raise CommandError(
                "%r conflicts with the name of an existing Python module and "
                "cannot be used as an app name. Please try another name." % app_name
            )

        # Auto create new destination path.
        if not os.path.exists(target) and os.path.exists(os.path.dirname(target)):
            os.mkdir(target)

        # Use different base template then Django's start_app.
        if not options.get('template'):
            root = os.path.dirname(fluent_contents.__file__)
            options['template'] = os.path.join(root, 'conf', 'plugin_template')

        # Create {{ model }} and {{ plugin }} settings.
        if not options['plugin']:
            # default converts "app_name" -> "AppNamePlugin"
            options['plugin'] = "{0}Plugin".format(app_name.replace('_', ' ').title().replace(' ', ''))

        if not options['model']:
            if options['plugin'].endswith('Plugin'):
                # default convert "AppNamePlugin" -> "AppNameItem"
                options['model'] = RE_PLUGIN.sub('Item', options['plugin'])
            else:
                options['model'] = "{0}Item".format(options['plugin'])

        super(Command, self).handle('app', app_name, target, **options)
