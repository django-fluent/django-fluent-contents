from django.core.management.base import BaseCommand, CommandError
from pprint import pformat
from micawber.exceptions import ProviderNotFoundException, ProviderException
from fluent_contents.plugins.oembeditem.backend import get_oembed_data


class Command(BaseCommand):
    args = '<url>'
    help = "Display the OEmbed results of an URL"

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Missing URL parameter")

        for url in args:
            try:
                data = get_oembed_data(url)
            except ProviderNotFoundException:
                self.stderr.write("* No OEmbed provider found for '{0}'!\n".format(url))
            except ProviderException as e:
                # Real urllib2 exception is sadly hidden by micawber.
                self.stderr.write("* {0}\n".format(e))
            else:
                self.stdout.write("* OEmbed data for '{0}':\n".format(url))

                for key in sorted(data.keys()):
                    self.stdout.write('  - {0}: {1}\n'.format(key, pformat(data[key])))
