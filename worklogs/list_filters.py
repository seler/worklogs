from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class StateListFilter(SimpleListFilter):
    template = "admin/state_list_filter.html"

    def lookups(self, request, model_admin):
        return (
#            (None, _('Yes')),
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
    dict = {
        'title': _('Display ') + unicode(state_name),
        'parameter_name': 'state_%d' % state_id,
        'state': state_id,
    }
    StateListFilters.append(type(name, bases, dict))
