from django.views.generic import DetailView

from fluent_contents.tests.testapp.models import PlaceholderFieldTestPage


class TestPageView(DetailView):
    model = PlaceholderFieldTestPage
    template_name = "testapp/testpage.html"
    # The context_object_name is set to the default variable that {% page_placeholder %} looks for.
    context_object_name = "page"
