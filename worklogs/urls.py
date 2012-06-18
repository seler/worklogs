# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from .views import task_start, task_stop, report

urlpatterns = patterns('',
    url(r'^$', report, name='report'),
)

task_admin_urls = patterns('',
    url(r'^start/(?P<object_id>\d+)/$', task_start, name='task_start'),
    url(r'^stop/(?P<object_id>\d+)/$', task_stop, name='task_stop'),
)
