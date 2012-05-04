# -*- coding: utf-8 -*-

#importy z pythona
import datetime

# importy z django
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from .managers import WorkLogManager


safe_storage_class = get_storage_class(settings.SAFE_FILE_STORAGE)
safe_storage = safe_storage_class()


def firstof(*items):
    for i in items:
        if i:
            return i


class WorkLog(models.Model):
    active = models.BooleanField(verbose_name=_(u'active'), unique=True)

    description = models.CharField(
                    max_length=1024,
                    verbose_name=_(u'description'))

    user = models.ForeignKey('auth.User',
                    verbose_name=_(u'user'),
                    related_name='worklogs')

    project = models.ForeignKey('Project',
                    verbose_name=_(u'project'),
                    related_name='worklogs')

    bugtracker = models.ForeignKey('BugTracker',
                    verbose_name=_(u'project'),
                    related_name='worklogs')

    bugtracker_object_id = models.CharField(
                    max_length=16,
                    verbose_name=_(u"bugtracker object id"))

    duration = models.PositiveIntegerField(
                    blank=True,
                    null=True,
                    verbose_name=_(u"duration"))

    add_date = models.DateTimeField(
#                    auto_now_add=True,
                    verbose_name=_(u'date added'))

    mod_date = models.DateTimeField(
#                    auto_now=True,
                    verbose_name=_(u'date modified'))

    objects = WorkLogManager()

    class Meta:
        verbose_name = _(u'work log')
        verbose_name_plural = _(u'work logs')
        ordering = ('-add_date',)
        get_latest_by = 'add_date'

    def __unicode__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('worklog', args=[self.pk])

    def start(self, description):
        if not self.active:
            # stop active WorkLog
            try:
                active_worklog = self.objects.active().get()
            except self.DoesNotExists:
                pass
            else:
                active_worklog.stop()
        else:
            # strop active WorkLogEntry
            active_entry = self.worklog_entries.filter(active=True).get()
            active_entry.active = False
            active_entry.save()

        # calculate duration
        self.duration = sum(map(lambda e: e.duration, self.worklog_entriels.all()))

        # mark self active
        self.active = True

        # and save
        self.save()

        # create new WorkLogEntry for this WorkLog
        WorkLogEntry.objects.create(worklog=self, description=description)

    def stop(self):
        pass


class WorkLogEntry(models.Model):
    active = models.BooleanField(
            default=True,
            unique=True,
            verbose_name=_(u'active'))

    description = models.CharField(
                    max_length=1024,
                    verbose_name=_(u'description'))

    worklog = models.ForeignKey('WorkLog',
                    verbose_name=_(u'worklog'),
                    related_name='worklog_entries')

    start = models.DateTimeField(
                    verbose_name=_(u'start time'))

    end = models.DateTimeField(
                    verbose_name=_(u'end time'))

    class Meta:
        verbose_name = _(u'work log entry')
        verbose_name_plural = _(u'work log entries')
        ordering = ('-start',)
        get_latest_by = 'start'

    def __unicode__(self):
        return self.description

    @property
    def duration(self):
        delta = self.end - self.start
        return int(round(delta.total_seconds()))

    @duration.setter
    def duration(self, seconds):
        self.end = self.start + datetime.timedelta(seconds=seconds)


class Project(models.Model):

    active = models.BooleanField(verbose_name=_(u'active'), unique=True)

    name = models.CharField(
                    max_length=64,
                    verbose_name=_(u'name'))

    class Meta:
        verbose_name = _(u'project')
        verbose_name_plural = _(u'projects')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project', args=[self.pk])


class BugTracker(models.Model):
    active = models.BooleanField(verbose_name=_(u'active'), unique=True)

    name = models.CharField(
                    max_length=64,
                    verbose_name=_(u'name'))

    url_pattern = models.CharField(
                    max_length=256,
                    verbose_name=_(u'url_pattern'))

    class Meta:
        verbose_name = _(u'bugtracker')
        verbose_name_plural = _(u'bugtrackers')

    def __unicode__(self):
        return self.name

