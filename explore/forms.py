from django import forms

class CommandForm(forms.Form):
    command_text = forms.CharField(max_length=512, help_text="")
