from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from simplecms.models import Page


def page_detail(request, path):
    stripped = path.strip('/') if path else ''
    stripped = stripped and u'/%s/' % stripped or '/'

    try:
        page = Page.objects.get(_cached_url=stripped)
    except Page.DoesNotExist:
        raise Http404("No page found for the path '%s'" % stripped)

    return render_to_response(page.template_name, {
        'simplecms_page': page,
    }, context_instance=RequestContext(request))
