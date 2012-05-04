# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import WorkLog, WorkLogEntry, Project, BugTracker


class WorkLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'mod_date'
    list_display = ('project', 'bugtracker', 'bugtracker_object_id', 'duration', 'add_date', 'mod_date', 'active')

admin.site.register(WorkLog, WorkLogAdmin)
admin.site.register((WorkLogEntry, Project, BugTracker))
