#-*- coding: utf-8 -*-

from django.template import Library

register = Library()


@register.filter
def seconds_to_hours(seconds, asd=4):
    return round(seconds / 3600., asd)


@register.filter
def seconds_to_readable(seconds):
    if seconds < 0:
        seconds = -seconds
        negative = True
    else:
        negative = False
    h = seconds / 3600
    m = seconds / 60 % 60
    s = seconds % 60
    ret = "{h}:{m:02}:{s:02}".format(**locals())
    ret = "{h}h {m}m {s}s".format(**locals())
    if negative:
        ret = '- ' + ret
    return ret


@register.filter
def seconds_to_time(seconds):
    if seconds < 0:
        seconds = -seconds
        negative = True
    else:
        negative = False
    h = seconds / 3600
    m = seconds / 60 % 60
    s = seconds % 60
    ret = "{h}:{m:02}".format(**locals())
    if negative:
        ret = '- ' + ret
    return ret


@register.filter
def date_to_hours(date):
    seconds = ((date.hour * 3600) + (date.minute * 60) + (date.second))
    return '{0}'.format(round(seconds / 3600., 4))
