from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from fluent_contents.extensions import HttpRedirectRequest


class HttpRedirectRequestMiddleware(MiddlewareMixin):
    """
    .. versionadded:: 1.0
    Middleware that handles requests redirects, requested by plugins using :func:`ContentPlugin.redirect() <fluent_contents.extensions.ContentPlugin.redirect>`.
    This needs to be added to :django:setting:`MIDDLEWARE_CLASSES` for redirects to work.

    .. admonition:: Some background:

       Since plugins can't return a :class:`~django.http.HttpResponseRedirect` response themselves,
       because they are part of the template rendering process.
       Instead, Python exception handling is used to abort the rendering and return the redirect.

       When :func:`ContentPlugin.redirect() <fluent_contents.extensions.ContentPlugin.redirect>` is called,
       a :class:`~fluent_contents.extensions.HttpRedirectRequest` exception is raised.
       This middleware handles the exception, and returns the proper redirect response.
    """

    def process_exception(self, request, exception):
        """
        Return a redirect response for the :class:`~fluent_contents.extensions.HttpRedirectRequest`
        """
        if isinstance(exception, HttpRedirectRequest):
            return HttpResponseRedirect(exception.url, status=exception.status)
        else:
            return None

    def process_template_response(self, request, response):
        """
        Patch a :class:`~django.template.response.TemplateResponse` object
        to handle the :class:`~fluent_contents.extensions.HttpRedirectRequest` exception too.
        """
        # The process_exception() is not called for TemplateResponse objects,
        # as these objects render outside the "try,call-view,except" block..
        response.render = _new_render(response)
        return response


def _new_render(response):
    """
    Decorator for the TemplateResponse.render() function
    """
    orig_render = response.__class__.render

    # No arguments, is used as bound method.
    def _inner_render():
        try:
            return orig_render(response)
        except HttpRedirectRequest as e:
            return HttpResponseRedirect(e.url, status=e.status)

    return _inner_render
