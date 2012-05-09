# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from .models import WorkLog, WorkLogEntry

current_year = lambda: datetime.datetime.now().isocalendar()[0]
current_week = lambda: datetime.datetime.now().isocalendar()[1]


def tofirstdayinisoweek(year, week):
    ret = datetime.datetime.strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
    if datetime.date(year, 1, 4).isoweekday() > 4:
        ret -= datetime.timedelta(days=7)
    return ret


@login_required
def worklog_start(request, object_id):
    worklog = WorkLog.objects.get(id=object_id)
    if request.user == worklog.user or request.user.is_superuser:
        # FIXME: zamienic na "user_passes_test"
        worklog.start()
        messages.success(request, _(u'WorkLog "{}" has been started.').format(worklog))
    else:
        messages.error(request, _(u'WorkLog "{}" has <b>not</b> been started. Insufficient permissions.').format(worklog))
    return HttpResponseRedirect('/worklogs/worklog/')


@login_required
def worklog_stop(request, object_id):
    worklog = WorkLog.objects.get(id=object_id)
    if request.user == worklog.user or request.user.is_superuser:
        # FIXME: zamienic na "user_passes_test"
        worklog.stop()
        messages.success(request, _(u'WorkLog "{}" has been stopped.').format(worklog))
    else:
        messages.error(request, _(u'WorkLog "{}" has <b>not</b> been stopped. Insufficient permissions.').format(worklog))
    return HttpResponseRedirect('/worklogs/worklog/')


@login_required
def report(request):

    get_from_date = request.GET.get('from')
    get_to_date = request.GET.get('to')

    year = current_year()
    week = current_week()

    if get_from_date:
        tmp = map(int, get_from_date.split('-'))
        from_date = datetime.datetime(*tmp)
    else:
        from_date = tofirstdayinisoweek(year, week)

    if get_to_date:
        tmp = map(int, get_to_date.split('-'))
        to_date = datetime.datetime(*tmp)
    else:
        to_date = from_date + datetime.timedelta(days=5)

    entries = WorkLogEntry.objects.in_range(from_date, to_date).filter(worklog__user=request.user)

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
                index = list(map(lambda a: a[0].id, worklogs_per_day[date]['worklogs'])).index(entry.worklog.id)
            except ValueError:
                worklogs_per_day[date]['worklogs'].append([entry.worklog, entry.duration])
            else:
                worklogs_per_day[date]['worklogs'][index][1] += entry.duration
            worklogs_per_day[date]['time'] += entry.duration
        else:
            worklogs_per_day[date] = {
                    'time': entry.duration,
                    'worklogs': [[entry.worklog, entry.duration]]
                }

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
    return render_to_response('worklogs/report.html', context_vars)
