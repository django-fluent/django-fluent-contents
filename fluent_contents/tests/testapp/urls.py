from django.contrib import admin
from django.urls import path

from . import views

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("testpage/<int:pk>/", views.TestPageView.as_view(), name="testpage")
    # url(r'^comments/', include('django.contrib.comments.urls')),
    # url(r'^forms/', include('form_designer.urls')),
]
