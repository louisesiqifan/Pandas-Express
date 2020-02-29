import traceback
import sys
import csv
import os

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

from score_assignment import get_dishes

# EXAMPLE_0 = {'level': 'easy',
#              'time': (30, 'total'), 'title': 'fried chicken',
#              'nutrition': {'calories': -1, 'protein': 1}}

TIME_CHOICES = [("total", "Total"), ("active", "Active")]

LEVEL_CHOICES = [("easy", "Easy"),
                 ("intermediate", "Intermediate"),
                 ("hard", "Hard")]

COLUMN_NAMES = {"id": 'ID',
                'name': "Recipe",
                'level': "Difficulty Level",
                'time_active': "Active Time",
                'time_total': "Total Time",
                'serving_size': "Serving Size",
                'calories': "Calories",
                'total_fat': "Total Fat",
                'directions': "Directions",
                'saturated_fat': "Saturated Fat",
                'cholesterol': "Cholesterol",
                'sodium': "Sodium",
                'total_carbohydrate': 'Total Carbohydrate',
                'dietary_fiber': 'Dietary Fiber',
                'sugars': 'Sugars',
                'protein': 'Protein',
                'potassium': 'Potassium'}


class Cooking_Time(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.ChoiceField(label='Mode', choices=TIME_CHOICES,
                                    required=False),)
        super(Cooking_Time, self).__init__(
            fields=fields,
            *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2:
            if data_list[0] is None or not data_list[1]:
                raise forms.ValidationError(
                    str(data_list))
            if data_list[0] < 0:
                raise forms.ValidationError(
                    'Big Brother is watching you bro.')
        return data_list


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search terms',
        help_text='e.g. fried chicken',
        required=False)
    time_and_mode = Cooking_Time(
        label='Cooking time:',
        help_text='e.g. 30 and total',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.NumberInput,
                     forms.widgets.Select(choices=TIME_CHOICES))))
    level = forms.MultipleChoiceField(label='Difficulty Level',
                                      choices=LEVEL_CHOICES,
                                      widget=forms.CheckboxSelectMultiple,
                                      required=False)
    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        print(form.is_valid())
        if form.is_valid():
            print("valid")
            # Convert form data to an args dictionary for find_courses
            args = {}
            if form.cleaned_data['query']:
                args['title'] = form.cleaned_data['query']

            level = form.cleaned_data['level']
            if level:
                args['level'] = level[0]

            time_and_mode = form.cleaned_data['time_and_mode']
            if time_and_mode:
                args['time'] = tuple(time_and_mode)

            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui= ' + str(args)

            print(args)
            try:
                res = get_dishes(args)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in get_dishes:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    # if res is None:
    #     context['result'] = None
    # elif isinstance(res, str):
    #     context['result'] = None
    #     context['err'] = res
    #     result = None
    # elif not _valid_result(res):
    #     context['result'] = None
    #     context['err'] = ('Return of find_courses has the wrong data type. '
    #                       'Should be a tuple of length 4 with one string and '
    #                       'three lists.')
    # else:
    if res is None:
        context['result'] = None
    else:
        columns, result = res
        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
        context['form'] = form

    return render(request, 'index.html', context)
