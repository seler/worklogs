from django.contrib.flatpages import models
from django.utils.translation import ugettext_lazy as _


class NewFlatPage(models.FlatPage):

    class Meta:
        proxy = True
        app_label = 'flatpages'
        verbose_name = _(u'flatpage')
        verbose_name_plural = _('flatpages')
