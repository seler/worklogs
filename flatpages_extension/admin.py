# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from django.contrib.flatpages.views import DEFAULT_TEMPLATE
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _


FLATPAGES_TINYMCE_CONFIG = {
    'theme': "advanced",
    'relative_urls': False,
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_blockformats': "p,address,blockquote,h1,h2,h3,h4,h5,h6,pre,code",
    'theme_advanced_toolbar_align': "left",

}
FLATPAGES_TINYMCE_WIDGET_ATTRS = {
    'cols': 80,
    'rows': 30,
}


class NewFlatPageForm(FlatpageForm):
    # set current site as initial
    sites = forms.ModelMultipleChoiceField(required=True,
                            queryset=Site.objects.all(),
                            widget=forms.widgets.CheckboxSelectMultiple,
                            initial=[Site.objects.get_current()])
    # set wysiwyg
    try:
        from tinymce.widgets import TinyMCE
    except ImportError:
        pass
    else:
        content = forms.CharField(widget=TinyMCE(
                                        attrs=FLATPAGES_TINYMCE_WIDGET_ATTRS,
                                        mce_attrs=FLATPAGES_TINYMCE_CONFIG),
                                  required=False)

    # template as choices
    template_name = forms.ChoiceField(required=False, label=_('Template'),
                                      choices=settings.FLATPAGES_TEMPLATE_NAME_CHOICES)

    class Meta:
        model = FlatPage


class NewFlatPageAdmin(FlatPageAdmin):
    form = NewFlatPageForm

    # move field `sites` to `Advanced options`
    fieldsets = FlatPageAdmin.fieldsets
    fieldsets[0][1]['fields'] = list(fieldsets[0][1]['fields'])
    fieldsets[0][1]['fields'].remove('sites')
    fieldsets[1][1]['fields'] = ('sites',) + fieldsets[1][1]['fields']

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, NewFlatPageAdmin)
