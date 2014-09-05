from django.http import HttpResponseRedirect
from fluent_contents.extensions import HttpRedirectRequest


class HttpRedirectRequestMiddleware(object):
    """
    .. versionadded:: 1.0
    Middleware that handles requests redirects

    Redirects by plugins are requested by :func:`ContentPlugin.redirect() <fluent_contents.extensions.ContentPlugin.redirect>`.
    However, plugins can't return a :class:`~django.http.HttpResponseRedirect` response themselves,
    as they are part of the template rendering process.
    Therefore, a :class:`~fluent_contents.extensions.HttpRedirectRequest` exception is raised instead.
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
