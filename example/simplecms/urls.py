from django.conf.urls import *

from . import views

urlpatterns = [url(r"^$|^(?P<path>.*/)$", views.page_detail, name="simplecms-page")]
