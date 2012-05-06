# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from .views import worklog_start, worklog_stop, report

urlpatterns = patterns('',
    url(r'^$', report, name='report'),
)

worklog_admin_urls = patterns('',
    url(r'^start/(?P<object_id>\d+)/$', worklog_start, name='worklog_start'),
    url(r'^stop/(?P<object_id>\d+)/$', worklog_stop, name='worklog_stop'),
)

