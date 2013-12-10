import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from .views import tofirstdayinisoweek, current_week, current_year


class StateListFilter(SimpleListFilter):
    template = "admin/state_list_filter.html"

    def lookups(self, request, model_admin):
        return (
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.exclude(state=self.state)

StateListFilters = []


from .models import Task


for state_id, state_name in Task.STATE_CHOICES:
    name = 'State%dListFilter' % state_id
    bases = (StateListFilter,)
    dic = {
        'title': _('Display ') + unicode(state_name),
        'parameter_name': 'state_%d' % state_id,
        'state': state_id,
    }
    StateListFilters.append(type(name, bases, dic))


class CurrentWeekListFilter(SimpleListFilter):
    title = _('current week only')
    parameter_name = 'current_week'

    def lookups(self, request, model_admin):
        return (
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() != 'no':
            year = current_year()
            week = current_week()
            from_date = tofirstdayinisoweek(year, week)
            to_date = from_date + datetime.timedelta(days=4)
            return queryset.filter(add_date__gte=from_date, add_date__lte=to_date)
