# -*- coding: utf-8 -*-

#importy z pythona
import datetime

# importy z django
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from .managers import WorkLogManager, WorkLogEntryManager


def firstof(*items):
    for i in items:
        if i:
            return i


class WorkLog(models.Model):
    STATE_NEW = 0
    STATE_IN_PROGRESS = 1
    STATE_WAITING = 2
    STATE_READY = 3
    STATE_RESOLVED = 4
    STATE_CLOSED = 5
    STATE_REJECTED = 6

    STATE_CHOICES = (\
        (STATE_NEW, _(u"new")),
        (STATE_IN_PROGRESS, _(u"in progress")),
        (STATE_WAITING, _(u"waiting")),
        (STATE_READY, _(u"ready")),
        (STATE_RESOLVED, _(u"resolved")),
        (STATE_CLOSED, _(u"closed")),
        (STATE_REJECTED, _(u"rejected")),
    )

    active = models.BooleanField(verbose_name=_(u'active'))

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
            blank=True,
            null=True,
            verbose_name=_(u'bugtracker'),
            related_name='worklogs')

    bugtracker_object_id = models.CharField(
            blank=True,
            null=True,
            max_length=16,
            verbose_name=_(u"bugtracker object id"))

    duration = models.PositiveIntegerField(
                    blank=True,
                    null=True,
                    verbose_name=_(u"duration"))

    add_date = models.DateTimeField(
                    auto_now_add=True,
                    verbose_name=_(u'date added'))

    mod_date = models.DateTimeField(
                    auto_now=True,
                    verbose_name=_(u'date modified'))

    state = models.PositiveSmallIntegerField(
                default=STATE_NEW,
                choices=STATE_CHOICES,
                verbose_name=_(u"state"))

    eta = models.DecimalField(
            blank=True,
            decimal_places=4,
            max_digits=8,
            null=True,
            verbose_name=_(u"eta (hours)"))

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

    def bugtracker_url(self):
        return self.bugtracker.url_pattern.format(id=self.bugtracker_object_id)

    def save(self, *args, **kwargs):
        new = True if not self.id else False
        ret = super(WorkLog, self).save(*args, **kwargs)
        if new:
            WorkLog.objects.stop_active()
            self.start()
        return ret

    def start(self, description=None):
        # stop active WorkLog
        WorkLog.objects.stop_active()

        # mark self active
        self.active = True
        self.save()

        # create new WorkLogEntry for this WorkLog
        WorkLogEntry.objects.create(worklog=self, description=description)

    def stop(self):
        try:
            active_entry = self.worklog_entries.filter(active=True).get()
        except WorkLogEntry.DoesNotExist:
            pass
        else:
            active_entry.stop()

        self.duration = self._calculate_duration()
        self.active = False
        self.save()

    def _calculate_duration(self):
        return sum(map(lambda e: e.duration, self.worklog_entries.all()))

    def update_duration(self):
        self.duration = self._calculate_duration()
        self.save()

    def time_left(self):
        if self.eta and self.duration:
            return self._seconds_to_readable(int(self.eta * 3600) - self.duration)
    time_left.short_description = _(u"time left")

    def _seconds_to_readable(self, seconds):
        if seconds < 0:
            seconds = -seconds
            negative = True
        else:
            negative = False
        h = seconds / 3600
        m = seconds / 60 % 60
        s = seconds % 60
        #return "{h}:{m}:{s}".format(**locals())
        ret = "{h}h {m}m {s}s".format(**locals())
        if negative:
            ret = '- ' + ret
        return ret

    def get_duration_display(self):
        if self.active or not self.duration:
            self.update_duration()
        return self._seconds_to_readable(self.duration)
    get_duration_display.short_description = _(u"duration")

    def get_eta_display(self):
        if self.eta:
            return self._seconds_to_readable(int(self.eta * 3600))
    get_eta_display.short_description = _(u"eta")


class WorkLogEntry(models.Model):
    active = models.BooleanField(
            default=True,
            verbose_name=_(u'active'))

    description = models.CharField(
                    blank=True,
                    null=True,
                    max_length=1024,
                    verbose_name=_(u'description'))

    worklog = models.ForeignKey('WorkLog',
                    verbose_name=_(u'worklog'),
                    related_name='worklog_entries')

    start = models.DateTimeField(
                    default=datetime.datetime.now,
                    verbose_name=_(u'start time'))

    end = models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name=_(u'end time'))

    objects = WorkLogEntryManager()

    class Meta:
        verbose_name = _(u'work log entry')
        verbose_name_plural = _(u'work log entries')
        ordering = ('-start',)
        get_latest_by = 'start'

    def stop(self):
        self.active = False
        self.end = datetime.datetime.now()
        self.save()

    @property
    def duration(self):
        if self.end:
            delta = self.end - self.start
        else:
            delta = datetime.datetime.now() - self.start
        return int(round(delta.total_seconds()))

    @duration.setter
    def duration(self, seconds):
        self.end = self.start + datetime.timedelta(seconds=seconds)


class Project(models.Model):

    active = models.BooleanField(verbose_name=_(u'active'))

    name = models.CharField(
                    max_length=64,
                    verbose_name=_(u'name'))

    url = models.URLField(
            blank=True,
            null=True,
            verbose_name=_(u"url"))

    class Meta:
        verbose_name = _(u'project')
        verbose_name_plural = _(u'projects')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project', args=[self.pk])


class BugTracker(models.Model):
    active = models.BooleanField(verbose_name=_(u'active'))

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
