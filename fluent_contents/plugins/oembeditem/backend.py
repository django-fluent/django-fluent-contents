from threading import Lock
from django.core.exceptions import ImproperlyConfigured
import micawber
from micawber.providers import Provider, ProviderRegistry
from . import appsettings

# Globally cached provider list,
# so embed.ly list is fetched only once.
_provider_list = None
_provider_lock = Lock()


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
    if appsettings.FLUENT_OEMBED_SOURCE == 'basic':
        registry = micawber.bootstrap_basic()
        # make sure http://youtu.be urls are also valid, see https://github.com/coleifer/micawber/pull/7
        registry.register('https?://(\S*.)?youtu(\.be/|be\.com/watch)\S*', Provider('http://www.youtube.com/oembed'))
        return registry
    elif appsettings.FLUENT_OEMBED_SOURCE == 'embedly':
        params = {}
        if appsettings.MICAWBER_EMBEDLY_KEY:
            params['key'] = appsettings.MICAWBER_EMBEDLY_KEY
        return micawber.bootstrap_embedly(**params)
    elif appsettings.FLUENT_OEMBED_SOURCE == 'list':
        # Fi
        registry = ProviderRegistry()
        for regex, provider in appsettings.FLUENT_OEMBED_PROVIDER_LIST:
            registry.register(regex, Provider(provider))
        return registry
    else:
        raise ImproperlyConfigured("Invalid value of FLUENT_OEMBED_SOURCE, only 'basic', 'list' or 'embedly' is supported.")


def has_provider_for_url(url):
    """
    Verify whether there is a provider for the URL.
    """
    registry = get_oembed_providers()
    return registry.provider_for_url(url) is not None


def get_oembed_data(url, max_width=None, max_height=None):
    """
    Fetch the OEmbed object, return the response as dictionary.
    """
    params = {}
    if max_width:  params['maxhwidth'] = max_width
    if max_height: params['maxheight'] = max_height

    registry = get_oembed_providers()
    return registry.request(url, **params)
