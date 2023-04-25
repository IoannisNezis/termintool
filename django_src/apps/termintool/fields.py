from django.conf import settings
from django.db import models
from django import forms


class WeekdayTimeField(models.Field):
    description = "Field for storing a weekday and time"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char(8)'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        else:
            day = int(value.split(", ")[0][2:-1])
            hour = int(value.split(", ")[1][1:-2])
            return (day, hour)

    def to_python(self, value):
        if isinstance(value, tuple):
            return value
        elif value is None:
            return None
        else:
            return tuple(value.split(' '))

    def get_prep_value(self, value):
        if value is None:
            return None
        else:
            return ' '.join(value)

    def formfield(self, **kwargs):
        defaults = {'widget': WeekdayTimeWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class WeekdayTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        days = settings.DAYS
        hours = [(str(i), '{0:02d}:00'.format(i)) for i in range(24)]
        time_widgets = [
            forms.Select(choices=settings.DAYS),
            forms.Select(choices=hours),
        ]
        super().__init__(time_widgets, attrs)

    def decompress(self, value):
        if value:
            return tuple(value.split(' '))
        else:
            return [None, None]

    def format_output(self, rendered_widgets):
        return '<div class="weekday-time-field">{0} {1}</div>'.format(*rendered_widgets)