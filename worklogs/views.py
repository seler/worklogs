# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic.dates import TodayArchiveView
from django.views.generic import ListView

from .models import WorkLog, WorkLogEntry

current_year = lambda: datetime.datetime.now().isocalendar()[0]
current_week = lambda: datetime.datetime.now().isocalendar()[1]


def tofirstdayinisoweek(year, week):
    ret = datetime.datetime.strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
    if datetime.date(year, 1, 4).isoweekday() > 4:
        ret -= datetime.timedelta(days=7)
    return ret


def worklog_start(request, object_id):
    worklog = WorkLog.objects.get(id=object_id)
    worklog.start()
    messages.success(request, 'WorkLog %s has been started.' % worklog)
    return HttpResponseRedirect('/worklogs/worklog/')


def worklog_stop(request, object_id):
    worklog = WorkLog.objects.get(id=object_id)
    worklog.stop()
    messages.success(request, 'WorkLog %s has been stopped.' % worklog)
    return HttpResponseRedirect('/worklogs/worklog/')


def weekly_report(request, year=current_year(), week=current_week()):
    from_date = tofirstdayinisoweek(year, week)
    to_date = from_date + datetime.timedelta(days=5)
    return report(request, from_date, to_date, extra_context={'week': week})


def report(request, from_date, to_date, extra_context=None):
    entries = WorkLogEntry.objects.in_range(from_date, to_date)

    time_per_project = {}
    time_per_worklog = []
    worklogs_per_day = {}

    for entry in entries:
        try:
            index = list(map(lambda a: a[0].id, time_per_worklog)).index(entry.worklog.id)
        except ValueError:
            time_per_worklog.append([entry.worklog, entry.duration])
        else:
            time_per_worklog[index][1] += entry.duration

        date = entry.start.date()
        if date in worklogs_per_day:
            try:
                index = list(map(lambda a: a[0].id, worklogs_per_day[date])).index(entry.worklog.id)
            except ValueError:
                worklogs_per_day[date].append([entry.worklog, entry.duration])
            else:
                worklogs_per_day[date][index][1] += entry.duration
        else:
            worklogs_per_day[date] = [[entry.worklog, entry.duration]]

        if entry.worklog.project in time_per_project:
            time_per_project[entry.worklog.project]['time'] += entry.duration
            try:
                index = list(map(lambda a: a[0].id, time_per_project[entry.worklog.project]['worklogs'])).index(entry.worklog.id)
            except ValueError:
                time_per_project[entry.worklog.project]['worklogs'].append([entry.worklog, entry.duration])
            else:
                time_per_project[entry.worklog.project]['worklogs'][index][1] += entry.duration
        else:
            time_per_project[entry.worklog.project] = {
                    'time': entry.duration,
                    'worklogs': [[entry.worklog, entry.duration]]
                }

    context_vars = {
        'from': from_date.date(),
        'to': to_date.date(),
        'worklogs_per_day': worklogs_per_day,
        'time_per_project': time_per_project,
        'time_per_worklog': time_per_worklog,
    }
    if extra_context:
        extra_context.update(context_vars)
        context_vars = extra_context
    return render_to_response('worklogs/report.html', context_vars)


class WorkLogTodayArchiveView(TodayArchiveView):
    model = WorkLog
    date_field = 'mod_date'


class WorkLogRecentView(ListView):
    queryset = WorkLog.objects.recent(days=3)
