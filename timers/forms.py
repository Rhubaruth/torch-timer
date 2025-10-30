from django.forms import ModelForm
from .models import Timer


class TimerForm(ModelForm):
    class Meta:
        model = Timer
        fields = ['title', 'init_duration']
