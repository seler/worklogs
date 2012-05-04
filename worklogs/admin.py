# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import WorkLog, WorkLogEntry, Project, BugTracker


admin.site.register((WorkLog, WorkLogEntry, Project, BugTracker))
