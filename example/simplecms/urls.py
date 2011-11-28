from django.conf.urls.defaults import *

urlpatterns = patterns('simplecms.views',
    url(r'^$|^(?P<path>.*/)$', 'page_detail', name='simplecms-page')
)
