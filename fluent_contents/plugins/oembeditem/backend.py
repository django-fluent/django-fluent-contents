import micawber
from micawber.providers import Provider


def get_oembed_providers():
    """
    Fetch the list of OEmbed providers.
    """
    registry = micawber.bootstrap_basic()
    # make sure http://youtu.be urls are also valid, see https://github.com/coleifer/micawber/pull/7
    registry.register('https?://(\S*.)?youtu(\.be/|be\.com/watch)\S*', Provider('http://www.youtube.com/oembed'))
    return registry


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
