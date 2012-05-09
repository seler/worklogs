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
        'bugtracker_link',
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
    search_fields = ('description', 'worklog_entries__description', 'bugtracker_object_id')

    def get_bugtracker_id(self, task):
        return '#%s' % task.bugtracker_object_id
    get_bugtracker_id.short_description = _(u"#")

    def get_duration_display(self, task):
        kwargs = {
            'duration_formatted': task.get_duration_display(),
            'duration': task.duration,
        }
        if task.active:
            return """<span class="task_duration d{duration}s">
    {duration_formatted}
</span>""".format(**kwargs)
        else:
            return kwargs.get('duration_formatted')
    get_duration_display.allow_tags = True
    get_duration_display.short_description = _(u"duration")

    def toggle_active_button(self, task):
        if task.active:
            link = """<a href="stop/{id}/" title="click to stop">{icon} stop</a>"""
        else:
            link = """<a href="start/{id}/" title="click to start">{icon} start</a>"""
        return link.format(id=task.id, icon=_boolean_icon(task.active))
    toggle_active_button.allow_tags = True
    toggle_active_button.short_description = _(u"toggle")

    def bugtracker_link(self, task):
        return """<a href="%s">%s/%s<a>""" % (task.bugtracker_url(), task.bugtracker.name, task.bugtracker_object_id)
    bugtracker_link.allow_tags = True
    bugtracker_link.short_description = _("bugtracker")

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
            "all": ("styles/worklog.css",)
        }
        js = (
            "http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js",
            "scripts/worklog.js",
        )


admin.site.register(Task, TaskAdmin)
admin.site.register((WorkLog, Project, BugTracker))
