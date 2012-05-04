# -*- coding: utf-8 -*-

from django.views.generic.dates import TodayArchiveView
from django.views.generic import ListView

from .models import WorkLog


class WorkLogTodayArchiveView(TodayArchiveView):
    model = WorkLog
    date_field = 'mod_date'


class WorkLogRecentView(ListView):
    queryset = WorkLog.objects.recent(days=3)
