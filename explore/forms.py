from django import forms

class SelectAreaForm(forms.Form):
    area_attrs = {
        'autofocus': 'autofocus',
        'autocomplete': 'off',
    }
    area_title = forms.CharField(
        max_length=512,
        label='Area Name ',
        label_suffix='>',
        widget=forms.TextInput(attrs=area_attrs),
    )

class CommandForm(forms.Form):
    command_attrs = {
        'autofocus': 'autofocus',
        'autocomplete': 'off',
    }
    command_text = forms.CharField(
        max_length=512,
        label='>',
        widget=forms.TextInput(attrs=command_attrs),
    )

class AreaForm(forms.Form):
    attrs = {
        'autofocus': 'autofocus',
        'cols': '80',
    }
    title = forms.CharField(label='Title')
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs=attrs),
    )

class ConnectionForm(forms.Form):
    attrs = {
        'autofocus': 'autofocus',
        'autocomplete': 'off',
    }
    destination_title = forms.CharField(
        label='Destination Area',
        label_suffix=' >',
        widget=forms.TextInput(attrs=attrs),
    )

class DeleteForm(forms.Form):
    pass
