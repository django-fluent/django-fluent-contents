from django.conf.urls import *

urlpatterns = patterns('simplecms.views',
    url(r'^$|^(?P<path>.*/)$', 'page_detail', name='simplecms-page')
)
