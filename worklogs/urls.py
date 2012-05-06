# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from .views import WorkLogTodayArchiveView, WorkLogRecentView, worklog_start, worklog_stop, weekly_report

urlpatterns = patterns('',
    url(r'^today/$', WorkLogTodayArchiveView.as_view()),
    url(r'^recent/$', WorkLogRecentView.as_view()),
    url(r'^weekly/$', weekly_report),
)

worklog_admin_urls = patterns('',
    url(r'^start/(?P<object_id>\d+)/$', worklog_start, name='worklog_start'),
    url(r'^stop/(?P<object_id>\d+)/$', worklog_stop, name='worklog_stop'),
)

