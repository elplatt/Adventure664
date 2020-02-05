from django import forms

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
