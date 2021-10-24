from pprint import pformat

from django.core.management.base import BaseCommand, CommandError
from micawber.exceptions import ProviderException, ProviderNotFoundException

from fluent_contents.plugins.oembeditem.backend import get_oembed_data


class Command(BaseCommand):
    args = "<url>"
    help = "Display the OEmbed results of an URL"

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Missing URL parameter")

        for url in args:
            try:
                data = get_oembed_data(url)
            except ProviderNotFoundException:
                self.stderr.write(f"* No OEmbed provider found for '{url}'!\n")
            except ProviderException as e:
                # Real urllib2 exception is sadly hidden by micawber.
                self.stderr.write(f"* {e}\n")
            else:
                self.stdout.write(f"* OEmbed data for '{url}':\n")

                for key in sorted(data.keys()):
                    self.stdout.write(f"  - {key}: {pformat(data[key])}\n")
