"""
Backend for fetching OEmbed data.

This module can also be used by other external apps.
"""
import threading
from micawber import Provider, ProviderRegistry, bootstrap_basic, bootstrap_embedly
from micawber.providers import bootstrap_noembed   # Export was missing in 0.2.6 patch, my mistake.
from django.core.exceptions import ImproperlyConfigured
from . import appsettings


__all__ = (
    'get_oembed_providers',
    'has_provider_for_url',
    'get_oembed_data',
)


# Globally cached provider list,
# so embed.ly list is fetched only once.
_provider_list = None
_provider_lock = threading.Lock()


def get_oembed_providers():
    """
    Get the list of OEmbed providers.
    """
    global _provider_list, _provider_lock
    if _provider_list is not None:
        return _provider_list

    # Allow only one thread to build the list, or make request to embed.ly.
    _provider_lock.acquire()
    try:
        # And check whether that already succeeded when the lock is granted.
        if _provider_list is None:
            _provider_list = _build_provider_list()
    finally:
        # Always release if there are errors
        _provider_lock.release()

    return _provider_list


def _build_provider_list():
    """
    Construct the provider registry, using the app settings.
    """
    registry = None
    if appsettings.FLUENT_OEMBED_SOURCE == 'basic':
        registry = bootstrap_basic()
    elif appsettings.FLUENT_OEMBED_SOURCE == 'embedly':
        params = {}
        if appsettings.MICAWBER_EMBEDLY_KEY:
            params['key'] = appsettings.MICAWBER_EMBEDLY_KEY
        registry = bootstrap_embedly(**params)
    elif appsettings.FLUENT_OEMBED_SOURCE == 'noembed':
        registry = bootstrap_noembed(nowrap=1)
    elif appsettings.FLUENT_OEMBED_SOURCE == 'list':
        # Fill list manually in the settings, e.g. to have a fixed set of supported secure providers.
        registry = ProviderRegistry()
        for regex, provider in appsettings.FLUENT_OEMBED_PROVIDER_LIST:
            registry.register(regex, Provider(provider))
    else:
        raise ImproperlyConfigured("Invalid value of FLUENT_OEMBED_SOURCE, only 'basic', 'list', 'noembed' or 'embedly' is supported.")

    # Add any extra providers defined in the settings
    for regex, provider in appsettings.FLUENT_OEMBED_EXTRA_PROVIDERS:
        registry.register(regex, Provider(provider))

    return registry


def has_provider_for_url(url):
    """
    Verify whether there is a provider for the URL.
    """
    registry = get_oembed_providers()
    return registry.provider_for_url(url) is not None


def get_oembed_data(url, max_width=None, max_height=None, **params):
    """
    Fetch the OEmbed object, return the response as dictionary.
    """
    if max_width:  params['maxwidth'] = max_width
    if max_height: params['maxheight'] = max_height

    registry = get_oembed_providers()
    return registry.request(url, **params)
