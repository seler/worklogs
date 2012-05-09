# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import Task


class TaskAddForm(forms.ModelForm):

    class Meta:
        model = Task
        exclude = ('active', 'duration')
