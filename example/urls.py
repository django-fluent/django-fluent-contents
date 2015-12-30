import django
from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/apps/tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),

    #url(r'^forms/', include('form_designer.urls')),

    url(r'^articles/', include('article.urls')),
    url(r'', include('simplecms.urls')),
]

if django.VERSION < (1, 7):
    urlpatterns = [
        url(r'^comments/', include('django.contrib.comments.urls')),
    ] + urlpatterns
else:
    urlpatterns = [
        url(r'^comments/', include('django_comments.urls')),
    ] + urlpatterns
