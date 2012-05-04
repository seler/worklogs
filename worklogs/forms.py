# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tinymce.widgets import TinyMCE

from .models import Video


class VideoForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80,
                                                        'rows': 30}))

    class Meta:
        model = Video

    def clean(self):
        cleaned_data = super(VideoForm, self).clean()
        file = cleaned_data.get('file', None)
        file_ftp = cleaned_data.get('file_ftp', None)
#        if not (file or file_ftp):
#            raise forms.ValidationError(_(u'proszę wskazać plik lub plik na ftp'))

        return cleaned_data

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            filename = file.name
            root, ext = os.path.splitext(filename)
            ext = ext.lstrip('.').lower()
            if ext not in settings.ALLOWED_VIDEO_FORMATS:
                raise forms.ValidationError(_(u'niepoprawny format pliku video'))
        return file

    def clean_file_ftp(self):
        file_ftp = self.cleaned_data.get('file_ftp')
        if file_ftp:
            filename = os.path.join(settings.FTP_MEDIA_ROOT, file_ftp)
            if not os.path.exists(filename):
                raise forms.ValidationError(_(u'plik nie znaleziony na ftp'))
        return file_ftp


class VideoAddForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(), required=False)
    tags = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Video
        exclude = ('slug', 'user', 'aspect_ratio', 'duration', 'pub_date', 'end_date',
                   'highlighted', 'imported', 'id_provider', 'authors',)
    """
    def clean(self):
        cleaned_data = super(VideoAddForm, self).clean()
        #file = cleaned_data.get('file', None)
        #file_ftp = cleaned_data.get('file_ftp', None)
        #if not (file or file_ftp):
        #    raise forms.ValidationError(_(u'proszę wskazać plik lub plik na ftp'))

        return cleaned_data
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            filename = file.name
            root, ext = os.path.splitext(filename)
            ext = ext.lstrip('.').lower()
            if ext not in settings.ALLOWED_VIDEO_FORMATS:
                raise forms.ValidationError(_(u'niepoprawny format pliku video'))
        return file

    def clean_file_ftp(self):
        file_ftp = self.cleaned_data.get('file_ftp')
        if file_ftp:
            filename = os.path.join(settings.FTP_MEDIA_ROOT, file_ftp)
            if not os.path.exists(filename):
                raise forms.ValidationError(_(u'plik nie znaleziony na ftp'))
        return file_ftp
    """

class VideoEditForm(forms.ModelForm):

    class Meta:
        model = Video
        #exclude = ('description','frame_time','rating','slug','user')
