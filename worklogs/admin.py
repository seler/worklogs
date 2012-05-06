# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, url
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from .models import WorkLog, WorkLogEntry, Project, BugTracker, State


class WorkLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'mod_date'
    list_display = (
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
    search_fields = ('description', 'worklog_entries__description')

    def toggle_active_button(self, worklog):
        if worklog.active:
            link = """<a href="stop/{id}/" title="click to stop">{icon} stop</a>"""
        else:
            link = """<a href="start/{id}/" title="click to start">{icon} start</a>"""
        return link.format(id=worklog.id, icon=_boolean_icon(worklog.active))
    toggle_active_button.allow_tags = True
    toggle_active_button.short_description = _(u"toggle")

    def bugtracker_link(self, worklog):
        return """<a href="%s">%s/%s<a>""" % (worklog.bugtracker_url(), worklog.bugtracker.name, worklog.bugtracker_object_id)
    bugtracker_link.allow_tags = True
    bugtracker_link.short_description = _("bugtracker")

    def project_link(self, worklog):
        url = worklog.project.url
        name = worklog.project.name
        if url:
            return """<a href="{url}">{name}</a>""".format(url=url, name=name)
        else:
            return name
    project_link.allow_tags = True
    project_link.short_description = _("project")

    def get_urls(self):
        urls = super(WorkLogAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^start/(?P<object_id>\d+)/$', self.start_view, name='worklog_start'),
            url(r'^stop/(?P<object_id>\d+)/$', self.stop_view, name='worklog_stop'),
        )
        return my_urls + urls

    def start_view(self, request, object_id):
        WorkLog.objects.get(id=object_id).start()
        return HttpResponseRedirect('/admin/worklogs/worklog/')

    def stop_view(self, request, object_id):
        WorkLog.objects.get(id=object_id).stop()
        return HttpResponseRedirect('/admin/worklogs/worklog/')


admin.site.register(WorkLog, WorkLogAdmin)
admin.site.register((WorkLogEntry, Project, BugTracker, State))
