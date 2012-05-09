# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from .models import Task, WorkLog

current_year = lambda: datetime.datetime.now().isocalendar()[0]
current_week = lambda: datetime.datetime.now().isocalendar()[1]


def tofirstdayinisoweek(year, week):
    ret = datetime.datetime.strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
    if datetime.date(year, 1, 4).isoweekday() > 4:
        ret -= datetime.timedelta(days=7)
    return ret


@login_required
def task_start(request, object_id):
    task = Task.objects.get(id=object_id)
    next = request.GET.get('next', '/')
    if request.user == task.user or request.user.is_superuser:
        # FIXME: zamienic na "user_passes_test"
        task.start()
        messages.success(request, _(u'Task "{}" has been started.').format(task))
    else:
        messages.error(request, _(u'Task "{}" has <b>not</b> been started. Insufficient permissions.').format(task))
    return HttpResponseRedirect(next)


@login_required
def task_stop(request, object_id):
    task = Task.objects.get(id=object_id)
    next = request.GET.get('next', '/')
    if request.user == task.user or request.user.is_superuser:
        # FIXME: zamienic na "user_passes_test"
        task.stop()
        messages.success(request, _(u'Task "{}" has been stopped.').format(task))
    else:
        messages.error(request, _(u'Task "{}" has <b>not</b> been stopped. Insufficient permissions.').format(task))
    return HttpResponseRedirect(next)


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

    entries = WorkLog.objects.in_range(from_date, to_date).filter(task__user=request.user)

    time_per_project = {}
    time_per_task = []
    tasks_per_day = {}

    for entry in entries:
        try:
            index = list(map(lambda a: a[0].id, time_per_task)).index(entry.task.id)
        except ValueError:
            time_per_task.append([entry.task, entry.duration])
        else:
            time_per_task[index][1] += entry.duration

        date = entry.start.date()
        if date in tasks_per_day:
            try:
                index = list(map(lambda a: a[0].id, tasks_per_day[date]['tasks'])).index(entry.task.id)
            except ValueError:
                tasks_per_day[date]['tasks'].append([entry.task, entry.duration])
            else:
                tasks_per_day[date]['tasks'][index][1] += entry.duration
            tasks_per_day[date]['time'] += entry.duration
        else:
            tasks_per_day[date] = {
                    'time': entry.duration,
                    'tasks': [[entry.task, entry.duration]]
                }

        if entry.task.project in time_per_project:
            time_per_project[entry.task.project]['time'] += entry.duration
            try:
                index = list(map(lambda a: a[0].id, time_per_project[entry.task.project]['tasks'])).index(entry.task.id)
            except ValueError:
                time_per_project[entry.task.project]['tasks'].append([entry.task, entry.duration])
            else:
                time_per_project[entry.task.project]['tasks'][index][1] += entry.duration
        else:
            time_per_project[entry.task.project] = {
                    'time': entry.duration,
                    'tasks': [[entry.task, entry.duration]]
                }

    context_vars = {
        'from': from_date.date(),
        'to': to_date.date(),
        'tasks_per_day': tasks_per_day,
        'time_per_project': time_per_project,
        'time_per_task': time_per_task,
    }
    return render_to_response('worklogs/report.html', context_vars)
