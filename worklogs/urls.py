# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from .views import WorkLogTodayArchiveView, WorkLogRecentView

urlpatterns = patterns('',
    url(r'^archive/today/$', WorkLogTodayArchiveView.as_view()),
    url(r'^recent/$', WorkLogRecentView.as_view()),
)
