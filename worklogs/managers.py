#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from django.db import models


class TaskManager(models.Manager):
    def recent(self, days=0):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=days)
        start = datetime.datetime.combine(start, datetime.time())
        end = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time())
        return self.get_query_set().filter(add_date__gte=start, mod_date__lt=end)

    def stop_active(self):
        task_queryset = self.get_query_set().filter(active=True)
        if task_queryset.exists():
            task = task_queryset.get()
            task.stop()
            return task
        else:
            return False


class WorkLogManager(models.Manager):
    def in_range(self, from_date, to_date):
        start = datetime.datetime.combine(from_date, datetime.time())
        end = datetime.datetime.combine(to_date + datetime.timedelta(days=1), datetime.time())

        return self.get_query_set().filter(
                models.Q(start__gte=start)
                & (models.Q(end__gte=start) | models.Q(end__isnull=True))
                & models.Q(start__lt=end)
                & (models.Q(end__lt=end) | models.Q(end__isnull=True)),
            )
