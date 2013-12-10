# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^report/', include('worklogs.urls')),
    url(r'^', include(admin.site.urls)),
)

urlpatterns += patterns('',
   (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
