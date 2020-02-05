from django import forms

class SelectAreaForm(forms.Form):
    area_title = forms.CharField(
        max_length=512,
        label='Area Name',
    )

class CommandForm(forms.Form):
    command_attrs = {
        'autofocus': 'autofocus',
        'autocomplete': 'off',
    }
    command_text = forms.CharField(
        max_length=512,
        label='>',
        widget=forms.TextInput(attrs=command_attrs
))
