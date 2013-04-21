from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/apps/tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^comments/', include('django.contrib.comments.urls')),
    #url(r'^forms/', include('form_designer.urls')),

    url(r'^articles/', include('article.urls')),
    url(r'', include('simplecms.urls')),
)
