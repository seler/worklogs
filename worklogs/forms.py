# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import WorkLog


class WorkLogAddForm(forms.ModelForm):

    class Meta:
        model = WorkLog
        exclude = ('active', 'duration')
