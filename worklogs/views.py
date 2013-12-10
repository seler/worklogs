# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from .models import Task, WorkLog
from .rozlicz import _rozlicz

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
        messages.success(request, _(u'Task "{0}" has been started.').format(task))
    else:
        messages.error(request, _(u'Task "{0}" has <b>not</b> been started. Insufficient permissions.').format(task))
    return HttpResponseRedirect(next)


@login_required
def task_stop(request, object_id):
    task = Task.objects.get(id=object_id)
    next = request.GET.get('next', '/')
    if request.user == task.user or request.user.is_superuser:
        # FIXME: zamienic na "user_passes_test"
        task.stop()
        messages.success(request, _(u'Task "{0}" has been stopped.').format(task))
    else:
        messages.error(request, _(u'Task "{0}" has <b>not</b> been stopped. Insufficient permissions.').format(task))
    return HttpResponseRedirect(next)


from django import forms


class TasksForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea())

from .mantis import make_mantis_task
import re
from django.shortcuts import render


@login_required
def make_tasks(request):
    next = request.GET.get('next', '/worklogs/task/')
    if request.method == 'POST':
        form = TasksForm(request.POST)
        if form.is_valid():
            tickets = re.findall(r'\d{5,8}', form.cleaned_data.get('message'))
            tickets = set(map(int, tickets))
            for ticket in tickets:
                try:
                    task = make_mantis_task(ticket)
                except Exception, e:
                    messages.error(request, _(u'Task "{0}" nie dodany. {1}').format(ticket, e))
                else:
                    messages.success(request, _(u'Task "{1}" dodany.').format(task.id, task.description))
            return HttpResponseRedirect(next)
    else:
        form = TasksForm()

    return render(request, 'worklogs/make_tasks.html', {
        'form': form,
    })


@login_required
def report(request):

    user = request.user

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
        to_date = from_date + datetime.timedelta(days=4)

    entries = WorkLog.objects.in_range(from_date, to_date).filter(task__user=user)

    time_per_project = {}
    time_per_task = []
    tasks_per_day = {}
    worklogs_plot = {}

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
                    'tasks': [[entry.task, entry.duration]],
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
                    'tasks': [[entry.task, entry.duration]],
                }

        # worklogs_plot

        ticket = "{0}{1}".format(entry.task.bugtracker.name, entry.task.bugtracker_object_id)
        start = entry.start
        end = entry.end if entry.end else datetime.datetime.now()
        row = (start, end)
        if ticket in worklogs_plot:
            worklogs_plot[ticket].append(row)
        else:
            worklogs_plot[ticket] = [row]

    tasks = Task.objects.filter(add_date__gte=from_date, add_date__lte=to_date)

    context_vars = {
        'tasks': tasks,
        'from': from_date.date(),
        'to': to_date.date(),
        'tasks_per_day': tasks_per_day,
        'time_per_project': time_per_project,
        'time_per_task': time_per_task,
        'tasks_by_status': sorted(time_per_task, key=lambda x: x[0].state),
        'worklogs_plot': worklogs_plot,
        'worklogs_plot_start': from_date.date() - datetime.timedelta(days=1),
        'worklogs_plot_end': to_date.date() + datetime.timedelta(days=1),
    }
    return render_to_response('worklogs/report.html', context_vars)


@login_required
def rozlicz(request, object_id):
    task = Task.objects.get(id=object_id)
    next = request.GET.get('next', '/')
    result = _rozlicz(task)
    if not result:
        messages.success(request, _(u'Task "{0}" accounted.').format(task))
    else:
        messages.error(request, _(u'Task "{0}" has`t been accounted. {1}').format(task, result))
    return HttpResponseRedirect(next)
