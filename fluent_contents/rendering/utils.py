"""
Internal - util functions for this 'rendering' package.
"""
import logging
import os
import six
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.test import RequestFactory
from django.conf import settings
from django.utils.translation import get_language
from django.core.cache import cache
from django.template.loader import select_template
from fluent_contents.extensions import ContentPlugin

try:
    from django.template.backends.django import Template as TemplateAdapter
except ImportError:
    TemplateAdapter = None

_log_functions = {
    logging.DEBUG: 'debug',
}


def add_media(dest, media):
    """
    Do what django.forms.Media.__add__() does without creating a new object.
    """
    dest.add_css(media._css)
    dest.add_js(media._js)


def get_placeholder_debug_name(placeholder):
    # TODO: Cheating here with knowledge of "fluent_contents.plugins.sharedcontent" package:
    #       prevent unclear message in <!-- no items in 'shared_content' placeholder --> debug output.
    if placeholder.slot == 'shared_content':
        sharedcontent = placeholder.parent
        return "shared_content:{0}".format(sharedcontent.slug)

    return placeholder.slot


def get_dummy_request(language=None):
    """
    Returns a Request instance populated with cms specific attributes.
    """
    if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != "*":
        host = settings.ALLOWED_HOSTS[0]
    else:
        host = Site.objects.get_current().domain

    request = RequestFactory().get("/", HTTP_HOST=host)
    request.session = {}
    request.LANGUAGE_CODE = language or settings.LANGUAGE_CODE
    # Needed for plugin rendering.
    request.current_page = None
    request.user = AnonymousUser()
    return request


def get_render_language(contentitem):
    """
    Tell which language should be used to render the content item.
    """
    plugin = contentitem.plugin

    if plugin.render_ignore_item_language \
    or (plugin.cache_output and plugin.cache_output_per_language):
        # Render the template in the current language.
        # The cache also stores the output under the current language code.
        #
        # It would make sense to apply this for fallback content too,
        # but that would be ambiguous however because the parent_object could also be a fallback,
        # and that case can't be detected here. Hence, better be explicit when desiring multi-lingual content.
        return get_language()  # Avoid switching the content,
    else:
        # Render the template in the ContentItem language.
        # This makes sure that {% trans %} tag output matches the language of the model field data.
        return contentitem.language_code


def is_template_updated(request, contentitem, cachekey):
    # For debugging only: tell whether the template is updated,
    # so the cached values can be ignored.

    plugin = contentitem.plugin
    if _is_method_overwritten(plugin, ContentPlugin, 'get_render_template'):
        # oh oh, really need to fetch the real object.
        # Won't be needed that often.
        contentitem = contentitem.get_real_instance()  # Need to determine get_render_template(), this is only done with DEBUG=True
        template_names = plugin.get_render_template(request, contentitem)
    else:
        template_names = plugin.render_template

    if not template_names:
        return False
    if isinstance(template_names, six.string_types):
        template_names = [template_names]

    # With TEMPLATE_DEBUG = True, each node tracks it's origin.
    template = select_template(template_names)
    if TemplateAdapter is not None and isinstance(template, TemplateAdapter):
        # Django 1.8 template wrapper
        template_filename = template.origin.name
    else:
        node0 = template.nodelist[0]
        attr = 'source' if hasattr(node0, 'source') else 'origin'  # attribute depends on object type

        try:
            template_filename = getattr(node0, attr)[0].name
        except (AttributeError, IndexError):
            return False

    cache_stat = cache.get(cachekey + ".debug-stat")
    current_stat = os.path.getmtime(template_filename)
    if cache_stat != current_stat:
        cache.set(cachekey + ".debug-stat", current_stat)
        return True


def _is_method_overwritten(object, cls, method_name):
    # This is the easiest Python 2+3 compatible way to check if something was overwritten,
    # assuming that it always happens in a different package (which it does in our case).
    # This avoids the differences with im_func, or __func__ not being available.
    #
    # This worked in 2.7:
    #   object.get_render_template.__func__ is not cls.get_render_template.__func__
    #
    # This worked in 3.2 and 3.3:
    #   object.get_render_template.__func__ is not cls.get_render_template
    #
    # This all fails in 3.4, so just checking the __module__ instead.
    method = getattr(object, method_name)
    cls_method = getattr(cls, method_name)
    return method.__module__ != cls_method.__module__


def _dummy_log(msg, *args, **kwargs):
    pass


def optimize_logger_level(logger, log_level):
    """
    At runtime, when logging is not active,
    replace the .debug() call with a no-op.
    """
    function_name = _log_functions[log_level]
    if getattr(logger, function_name) is _dummy_log:
        return False

    is_level_logged = logger.isEnabledFor(log_level)
    if not is_level_logged:
        setattr(logger, function_name, _dummy_log)

    return is_level_logged
