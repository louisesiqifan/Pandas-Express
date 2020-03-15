from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from manage_user import find_user, save_current_user, create_new_user
from reset_db import reset_db


CHOICES = [(1, 'New User'), (0, 'Comeback User')]


class Text(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(),
                  forms.ChoiceField(label='Mode', choices=CHOICES,
                                    required=True),)
        super(Text, self).__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2:
            if data_list[0] is None or not data_list[1]:
                return None
        return data_list


class SearchForm(forms.Form):
    query = Text(
        label='Username',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.TextInput,
                     forms.widgets.Select(choices=CHOICES)))
        )


def login(request):
    user = None
    context = {}
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            if request.GET.get('save'):
                username = form.cleaned_data['query'][0]
                create = int(form.cleaned_data['query'][1])
                exist = find_user(username)

                if create:
                    if exist:
                        raise ValueError('User Already Exists.')
                    else:
                        create_new_user(username)
                        user = username
                else:
                    if not exist:
                        raise ValueError('User does not exist, are you sure you entered the right name?')
                    else:
                        user = username
                save_current_user(username)
            elif request.GET.get('delete'):
                reset_db()
    else:
        form = SearchForm()

    context['form'] = form

    return render(request, 'login.html', context)