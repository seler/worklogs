#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from django.db import models


class WorkLogManager(models.Manager):
    def recent(self, days=0):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=days)
        start = datetime.datetime.combine(start, datetime.time())
        end = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time())
        return self.get_query_set().filter(add_date__gte=start, mod_date__lt=end)

    def stop_active(self):
        worklog_queryset = self.get_query_set().filter(active=True)
        if worklog_queryset.exists():
            worklog = worklog_queryset.get()
            worklog.stop()
            return worklog
        else:
            return False


class WorkLogEntryManager(models.Manager):
    def in_range(self, from_date, to_date):
        start = datetime.datetime.combine(from_date, datetime.time())
        end = datetime.datetime.combine(to_date + datetime.timedelta(days=1), datetime.time())

        return self.get_query_set().filter(
                models.Q(start__gte=start)
                & models.Q(end__gte=start)
                & models.Q(start__lt=end)
                & models.Q(end__lt=end)
            )

