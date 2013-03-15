# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from .models import Task, WorkLog, Project, BugTracker, Note
from .urls import task_admin_urls
from .forms import TaskAddForm
from .list_filters import StateListFilters
from django.contrib import messages


class WorkLogInlineAdmin(admin.TabularInline):
    model = WorkLog
    extra = 0
    max_num = 0


class NoteInlineAdmin(admin.StackedInline):
    model = Note
    extra = 0
    fields = (('add_date', 'mod_date'), 'note')
    readonly_fields = ('add_date', 'mod_date')


class TaskAdmin(admin.ModelAdmin):
    add_form = TaskAddForm
    date_hierarchy = 'mod_date'
    list_display = (
        'get_bugtracker_id',
        'description',
        'project_link',
        'get_bugtracker_link',
        'get_duration_display',
        'mod_date',
        'state',
        'toggle_active_button',
        'accounted',
    )
    ordering = ('-add_date',)
    inlines = (WorkLogInlineAdmin, NoteInlineAdmin)
    list_editable = ('state',)
    list_filter = StateListFilters + ['project', 'state', 'bugtracker']
    list_select_related = True
    search_fields = ('description',
                     'worklogs__description',
                     'bugtracker_object_id')
    save_on_top = True

    def get_duration_display(self, task):
        kwargs = {
            'duration_formatted': task.get_duration_display(),
            'duration': task.duration,
            'dupation': round(task.duration / 3600., 3),
        }
        if task.active:
            return """<span class="duration d{duration}s">
    {duration_formatted}
    </span><br /><span class="dupation">{dupation}</span>""".format(**kwargs)
        else:
            return """{duration_formatted}<br />{dupation}""".format(**kwargs)
    get_duration_display.allow_tags = True
    get_duration_display.short_description = _(u"duration")

    def accounted(self, task):
        if task.worklogs.count() and task.duration:
            a_n = task.worklogs.filter(accounted=True).count() / float(task.worklogs.count()) * 100.
            a_t = sum(map(lambda w: w.duration,
                          task.worklogs.filter(accounted=True))) / float(task.duration) * 100.
            return "<span class=\"accounted %s\">" \
                   "<a href=\"/worklogs/worklog/?task__id__exact=%d\">" \
                   "time: %d%%<br>worklogs: %d%%</a><span>" % \
                   ('good' if a_n == 100. else 'bad', task.id, a_t, a_n)
        else:
            return '-'
    accounted.short_description = _(u"accounted")
    accounted.allow_tags = True

    def toggle_active_button(self, task):
        if task.active:
            link = "<a href=\"/worklogs/task/stop/{id}/?next=/worklogs/task/\"" \
                   "title=\"click to stop\">{icon} stop</a>"
        else:
            link = "<a href=\"/worklogs/task/start/{id}/?next=/worklogs/task/\"" \
                   "title=\"click to start\">{icon} start</a>"
        return link.format(id=task.id, icon=_boolean_icon(task.active))
    toggle_active_button.allow_tags = True
    toggle_active_button.short_description = _(u"toggle")

    def get_bugtracker_link(self, task):
        if task.bugtracker:
            return """<a href="%s">%s/%s<a>""" % (task.bugtracker_url(),
                                                  task.bugtracker.name,
                                                  task.bugtracker_object_id)
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
                'formfield_callback': self.get_formfield_callback(request),
            })
        defaults.update(kwargs)
        return super(TaskAdmin, self).get_form(request, obj, **defaults)

    def get_formfield_callback(self, request):
        current_project_id = request.session.get('current_project_id', None)
        current_bugtracker_id = request.session.get('current_bugtracker_id', None)
        user_id = request.user.id

        def callback(field, **kwargs):
            formfield = field.formfield(**kwargs)
            if field.name == 'project':
                formfield.initial = current_project_id
            if field.name == 'bugtracker':
                formfield.initial = current_bugtracker_id
            if field.name == 'user':
                formfield.initial = user_id
            return formfield

        return callback

    def get_urls(self):
        urls = super(TaskAdmin, self).get_urls()
        return task_admin_urls + urls

    def save_model(self, request, obj, form, change):
        try:
            request.session['current_project_id'] = obj.project.id
        except AttributeError:
            pass
        try:
            request.session['current_bugtracker_id'] = obj.bugtracker.id
        except AttributeError:
            pass
        obj.update_duration()

    class Media:
        css = {
            "all": ("worklogs/styles/admin.css", ),
        }
        js = (
            "http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js",
            "worklogs/scripts/admin.js",
        )


from .rozlicz import _rozlicz


def rozlicz_action(modeladmin, request, queryset):
    for obj in queryset:
        result = _rozlicz(obj)
        if not result:
            messages.success(request, _(u'Task "{0}" accounted for {1}.').format(obj.task, obj.get_duration_display()))
        else:
            messages.error(request, _(u'Task "{0}" not accounted. {1}').format(obj.task, result))
rozlicz_action.short_description = "Rozlicz"


class WorkLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = (
        'get_description',
        'task_link',
        'project_link',
        'bugtracker_link',
        'get_duration_display',
        'start',
        'end',
        'toggle_active_button',
        'accounted',
    )
    list_editable = ('start', 'end')
    list_filter = ('task__project', 'accounted', 'task__state', 'task__bugtracker', 'task')
    list_select_related = True
    search_fields = ('description', 'worklog__description', 'worklog__bugtracker_object_id')
    actions = [rozlicz_action]
    save_on_top = True

    def get_bugtracker_id(self, worklog):
        return '#%s' % worklog.task.bugtracker_object_id
    get_bugtracker_id.short_description = _(u"#")

    def get_description(self, worklog):
        return worklog.description if worklog.description else worklog.task.description
    get_description.short_description = _(u"description")

    def get_duration_display(self, worklog):
        kwargs = {
            'duration_formatted': worklog.get_duration_display(),
            'duration': worklog.duration,
            'dupation': round(worklog.duration / 3600., 3),
        }
        if worklog.active:
            return """<span class="duration d{duration}s">
    {duration_formatted}
    </span><br /><span class="dupation">{dupation}</span>""".format(**kwargs)
        else:
            return """{duration_formatted}<br />{dupation}""".format(**kwargs)
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
        if worklog.task.bugtracker:
            return """<a href="%s">%s/%s<a>""" % (worklog.task.bugtracker_url(), worklog.task.bugtracker.name, worklog.task.bugtracker_object_id)
    bugtracker_link.allow_tags = True
    bugtracker_link.short_description = _("bugtracker")

    def task_link(self, worklog):
        return """<a href="/worklogs/task/%d/">%s<a>""" % (worklog.task.id, worklog.task.__unicode__())
    task_link.allow_tags = True
    task_link.short_description = _("task")

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
            "all": ("worklogs/styles/admin.css", ),
        }
        js = (
            "http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js",
            "worklogs/scripts/admin.js",
        )


admin.site.register(Task, TaskAdmin)
admin.site.register(WorkLog, WorkLogAdmin)
admin.site.register((Project, BugTracker))
