from django.conf.urls import url
from django.contrib import admin

from . import views

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^testpage/(?P<pk>\d+)/$', views.TestPageView.as_view(), name='testpage')

    #url(r'^comments/', include('django.contrib.comments.urls')),
    #url(r'^forms/', include('form_designer.urls')),
]
