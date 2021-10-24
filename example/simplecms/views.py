from django.http import Http404
from django.shortcuts import render
from django.template.context import RequestContext
from simplecms.models import Page


def page_detail(request, path):
    stripped = path.strip("/") if path else ""
    stripped = stripped and "/%s/" % stripped or "/"

    try:
        page = Page.objects.get(_cached_url=stripped)
    except Page.DoesNotExist:
        raise Http404("No page found for the path '%s'" % stripped)

    return render(request, page.template_name, {"simplecms_page": page})
