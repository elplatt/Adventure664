from django import forms

class ItemForm(forms.Form):
    item_attrs = {
        'autofocus': 'autofocus',
        'autocomplete': 'off',
    }
    item_title = forms.CharField(
        max_length=64,
        label='Item Title',
        widget=forms.TextInput(attrs=item_attrs),
    )
    short_description = forms.CharField(
        max_length=256,
        label='Short Description',
        widget=forms.TextInput(attrs={ 'autocomplete': 'off' }),
    )
    long_description = forms.CharField(
        label='Long Description',
        widget=forms.Textarea(),
    )

