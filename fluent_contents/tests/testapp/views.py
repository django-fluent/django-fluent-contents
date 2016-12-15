from django.views.generic import DetailView

from fluent_contents.tests.testapp.models import PlaceholderFieldTestPage


class TestPageView(DetailView):
    model = PlaceholderFieldTestPage
    template_name = "testapp/testpage.html"
    context_object_name = 'page'  # the default variable {% page_placeholder %} looks for.
