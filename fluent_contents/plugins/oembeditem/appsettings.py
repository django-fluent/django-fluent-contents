from django.conf import settings


# Define the source for the OEmbed provider list.
# By default, use a fixed set of providers, to avoid random other HTML content in the web site.
FLUENT_OEMBED_SOURCE = getattr(settings, 'FLUENT_OEMBED_SOURCE', 'basic')   # basic, embedly, noembed, list

# Allow to extend any source, whether it's basic/embedly/noembed/list
FLUENT_OEMBED_EXTRA_PROVIDERS = tuple(getattr(settings, 'FLUENT_OEMBED_EXTRA_PROVIDERS', ()))

# Before micawber 0.2.6 the default source was "list".
# However, micawber contains a more up-to-date list nowadays, so it doesn't make sense to keep a list here.
FLUENT_OEMBED_PROVIDER_LIST = getattr(settings, 'FLUENT_OEMBED_PROVIDER_LIST', ())

# Keep this for backwards compatibility, it's no longer advertised in the docs.
FLUENT_OEMBED_PROVIDER_LIST += tuple(getattr(settings, 'FLUENT_OEMBED_PROVIDER_LIST_EXTRA', ()))

# Embedly API key
MICAWBER_EMBEDLY_KEY = getattr(settings, 'MICAWBER_EMBEDLY_KEY', None)
