import traceback
import sys
import csv
import os

from functools import reduce
from operator import and_
from django.shortcuts import render
from django import forms
from django.http import HttpResponse
from score_assignment import get_dish, get_dishes
from django.template import Template



TIME_CHOICES = [("total", "Total"), ("active", "Active")]

LEVEL_CHOICES = [("easy", "Easy"),
                 ("intermediate", "Intermediate"),
                 ("advanced", "Advanced")]

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
                return None

        return data_list


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search terms',
        help_text='Try Fried Chicken!',
        required=False)
    time_and_mode = Cooking_Time(
        label='Cooking Time',
        help_text='30 minutes in total or more?',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.NumberInput,
                     forms.widgets.Select(choices=TIME_CHOICES))))
    level = forms.MultipleChoiceField(label='Difficulty Level',
                                      choices=LEVEL_CHOICES,
                                      widget=forms.CheckboxSelectMultiple,
                                      required=False)
    # show_args = forms.BooleanField(label='Show args_to_ui',
    #                                required=False)


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        form = SearchForm(request.GET)
        # print("request get:", request.GET)
        # print("Input:", form.data)
        # print("Valid:", form.is_valid())
        # print("Error:", form.errors)

        if form.is_valid():
            # print(form.cleaned_data)

            args = {}
            if form.cleaned_data['query']:
                args['title'] = form.cleaned_data['query']

            level = form.cleaned_data['level']
            if level:
                args['level'] = level[0]

            time_and_mode = form.cleaned_data['time_and_mode']
            if time_and_mode:
                args['time'] = tuple(time_and_mode)

            # if form.cleaned_data['show_args']:
            #     context['args'] = 'args_to_ui= ' + str(args)

            try:
                print(args)
                res = get_dishes(args)
                print("result:", res)
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


def get_detail(request):
    result=request.GET
    recipe_id = list(result.keys())[0]
    recipe = get_dish(int(recipe_id))
    html = '''
    <html>
        <link rel="stylesheet" type="text/css" href="../static/detail.css">
        <link href="https://fonts.googleapis.com/css?family=Quicksand:300,500" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=0.67">
        <head>
            <title>{0}</title>
        </head>
        <body>
            <div id="header">
                <h1>{0}</h1>
            </div>

            <div id="time">
                <p>Total time: {1} min</p>
            </div>

            <div id="ingredient">

            </div>

            <div id="direction">
                <h3> Direction: </h3>
                    <p> {2} </p>
            </div>

            <form method="get" action="{{ % url 'home'% }}">
            <input type="back" class="button" value="Back to search"/>
            </form>

            <div id="footer">
                 <h2>Presented by Team AttributeError</h2>
            </div>
        </body>
    </html>
    '''.format(recipe[1], recipe[3], recipe[-1])
    return HttpResponse(html)
