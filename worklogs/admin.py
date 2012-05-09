# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from .models import Task, WorkLog, Project, BugTracker
from .urls import task_admin_urls
from .forms import TaskAddForm


class TaskAdmin(admin.ModelAdmin):
    add_form = TaskAddForm
    date_hierarchy = 'mod_date'
    list_display = (
        'get_bugtracker_id',
        'description',
        'project_link',
        'get_bugtracker_link',
        'get_duration_display',
        'time_left',
        'get_eta_display',
        'add_date',
        'mod_date',
        'state',
        'toggle_active_button',
    )
    list_editable = ('state',)
    list_filter = ('project', 'state', 'bugtracker')
    list_select_related = True
    search_fields = ('description', 'worklogs__description', 'bugtracker_object_id')

    def get_duration_display(self, task):
        kwargs = {
            'duration_formatted': task.get_duration_display(),
            'duration': task.duration,
        }
        if task.active:
            return """<span class="duration d{duration}s">
    {duration_formatted}
</span>""".format(**kwargs)
        else:
            return kwargs.get('duration_formatted')
    get_duration_display.allow_tags = True
    get_duration_display.short_description = _(u"duration")

    def toggle_active_button(self, task):
        if task.active:
            link = """<a href="/worklogs/task/stop/{id}/?next=/worklogs/task/" title="click to stop">{icon} stop</a>"""
        else:
            link = """<a href="/worklogs/task/start/{id}/?next=/worklogs/task/" title="click to start">{icon} start</a>"""
        return link.format(id=task.id, icon=_boolean_icon(task.active))
    toggle_active_button.allow_tags = True
    toggle_active_button.short_description = _(u"toggle")

    def get_bugtracker_link(self, task):
        return """<a href="%s">%s/%s<a>""" % (task.bugtracker_url(), task.bugtracker.name, task.bugtracker_object_id)
    get_bugtracker_link.allow_tags = True
    get_bugtracker_link.short_description = _("bugtracker")

    def project_link(self, task):
        url = task.project.url
        name = task.project.name
        if url:
            return u"""<a href="{url}">{name}</a>""".format(url=url, name=name)
        else:
            return name
    project_link.allow_tags = True
    project_link.short_description = _("project")

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
            })
        defaults.update(kwargs)
        return super(TaskAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        urls = super(TaskAdmin, self).get_urls()
        return task_admin_urls + urls

    class Media:
        css = {
            "all": ("worklogs/styles/admin.css",)
        }
        js = (
            "http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js",
            "worklogs/scripts/admin.js",
        )


class WorkLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = (
       'task',
       'get_description',
       'project_link',
       'bugtracker_link',
       'get_duration_display',
       'start',
       'end',
       'toggle_active_button',
    )
#    list_editable = ('state',)
    list_filter = ('task__project', 'task__state', 'task__bugtracker', 'task')
    list_select_related = True
    search_fields = ('description', 'worklog__description', 'worklog__bugtracker_object_id')

    def get_bugtracker_id(self, worklog):
        return '#%s' % worklog.task.bugtracker_object_id
    get_bugtracker_id.short_description = _(u"#")

    def get_description(self, worklog):
        return worklog.description if worklog.description else worklog.task.description

    def get_duration_display(self, worklog):
        kwargs = {
            'duration_formatted': worklog.get_duration_display(),
            'duration': worklog.duration,
        }
        if worklog.active:
            return """<span class="duration d{duration}s">
    {duration_formatted}
</span>""".format(**kwargs)
        else:
            return kwargs.get('duration_formatted')
    get_duration_display.allow_tags = True
    get_duration_display.short_description = _(u"duration")

    def toggle_active_button(self, worklog):
        if worklog.active:
            link = """<a href="/worklogs/task/stop/{id}/?next=/worklogs/worklog/" title="click to stop">{icon} stop</a>"""
        else:
            link = """<a href="/worklogs/task/start/{id}/?next=/worklogs/worklog/" title="click to start">{icon} start</a>"""
        return link.format(id=worklog.task.id, icon=_boolean_icon(worklog.active))
    toggle_active_button.allow_tags = True
    toggle_active_button.short_description = _(u"toggle")

    def bugtracker_link(self, worklog):
        return """<a href="%s">%s/%s<a>""" % (worklog.task.bugtracker_url(), worklog.task.bugtracker.name, worklog.task.bugtracker_object_id)
    bugtracker_link.allow_tags = True
    bugtracker_link.short_description = _("bugtracker")

    def project_link(self, worklog):
        url = worklog.task.project.url
        name = worklog.task.project.name
        if url:
            return u"""<a href="{url}">{name}</a>""".format(url=url, name=name)
        else:
            return name
    project_link.allow_tags = True
    project_link.short_description = _("project")

#    def get_form(self, request, obj=None, **kwargs):
#        defaults = {}
#        if obj is None:
#            defaults.update({
#                'form': self.add_form,
#            })
#        defaults.update(kwargs)
#        return super(TaskAdmin, self).get_form(request, obj, **defaults)
#
#    def get_urls(self):
#        urls = super(TaskAdmin, self).get_urls()
#        return task_admin_urls + urls

    class Media:
        css = {
            "all": ("worklogs/styles/admin.css",)
        }
        js = (
            "http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js",
            "worklogs/scripts/admin.js",
        )


admin.site.register(Task, TaskAdmin)
admin.site.register(WorkLog, WorkLogAdmin)
admin.site.register((Project, BugTracker))
