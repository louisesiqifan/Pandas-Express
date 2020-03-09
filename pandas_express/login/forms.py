from django import forms
from models import User


class SearchForm(forms.Form):
    user = Text(
        label='Username and Password',
        required=True,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.TextInput,
                     forms.widgets.TextInput))
        )
