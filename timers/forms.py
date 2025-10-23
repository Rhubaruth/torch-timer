from django.forms import ModelForm
from .models import Timer


class TimerForm(ModelForm):
    class Meta:
        model = Timer
        fields = ['init_duration']
