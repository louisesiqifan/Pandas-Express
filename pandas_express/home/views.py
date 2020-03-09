from functools import reduce
from operator import and_
from django.shortcuts import render
from django import forms
from django.http import HttpResponse
from score_assignment import get_dish, get_dishes, get_dish_ingredient
from django.template import Template
from plotter import plot_one_nutrition, plot_two_nutrition

TIME_CHOICES = [("total", "Total"), ("active", "Active")]
LEVEL_CHOICES = [("easy", "Easy"),
                 ("intermediate", "Intermediate"),
                 ("advanced", "Advanced")]
IMPORTANCE_CHOICES = [(1, 'Default'), (10, 'Important')]
TERM_IMPORTANCE_CHOICES = [(10, 'Default'), (50, 'Important')]
ADVANCE_CHOICES = [(1, 'Yes')]
NUTRITION_CHOICES = [(-1, 'Low'), (1,"High")]
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
                'total_carbohydrate': 'Total Carb',
                'dietary_fiber': 'Dietary Fiber',
                'sugars': 'Sugars',
                'protein': 'Protein',
                'potassium': 'Potassium'}
NUTRITION_PLOT_CHOICE = [('calories', "Calories"),
                         ('total_fat', "Total Fat"),
                         ('total_carbohydrate', 'Total Carb'),
                         ('sugars', 'Sugars'),
                         ('protein', 'Protein'),
                         ('potassium', 'Potassium')]

######## FORM CLASSES **********

class Text(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(),
                  forms.ChoiceField(label='Mode', choices=TERM_IMPORTANCE_CHOICES,
                                    required=False),)
        super(Text, self).__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2:
            if data_list[0] is None or not data_list[1]:
                return None
        return data_list


class Cooking_Time(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.ChoiceField(label='Mode', choices=TIME_CHOICES,
                                    required=False),
                  forms.ChoiceField(label='Mode', choices=IMPORTANCE_CHOICES,
                                    required=False),)
        super(Cooking_Time, self).__init__(
            fields=fields,
            *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 3:
            if data_list[0] is None or not data_list[1]:
                return None
        return data_list


########## SEARCH PAGE ##########

class SearchForm(forms.Form):
    query = Text(
        label='Search Terms',
        help_text='Try Fried Chicken!',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.TextInput,
                     forms.widgets.Select(choices=TERM_IMPORTANCE_CHOICES)))
        )

    time_and_mode = Cooking_Time(
        label='Cooking Time',
        help_text='30 minutes in total or more?',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.NumberInput,
                     forms.widgets.Select(choices=TIME_CHOICES),
                     forms.widgets.Select(choices=IMPORTANCE_CHOICES)))
        )

    level = forms.MultipleChoiceField(label='Difficulty Level',
                                      choices=LEVEL_CHOICES,
                                      widget=forms.CheckboxSelectMultiple,
                                      required=False)

    #show_args = forms.BooleanField(label='Show args_to_ui',
    #                                required=False)

def search(request):
    context = {}
    res = None
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            args = {}
            weight = {}
            if form.cleaned_data['query']:
                args['title'] = form.cleaned_data['query'][0]
                weight['title'] = int(form.cleaned_data['query'][1])

            level = form.cleaned_data['level']
            if level:
                args['level'] = level[0]

            time_and_mode = form.cleaned_data['time_and_mode']
            if time_and_mode:
                print(time_and_mode)
                args['time'] = tuple(time_and_mode[:-1])
                weight['time'] = int(time_and_mode[-1])

            #if form.cleaned_data['show_args']:
            #    context['args'] = 'args_to_ui= ' + str(args)
            #raise ValueError(str(weight))

            try:
                res = get_dishes(args, weight=weight)
                print(res)
            except Exception as e:
                print('Exception caught')
                res = None
    else:
        form = SearchForm()

    if res is None:
        context['result'] = None
    else:
        columns, result = res
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
        context['form'] = form

    return render(request, 'home.html', context)


####### AdvanceForm #######

class AdvanceForm(forms.Form):

    query = Text(
        label='Search Terms',
        help_text='Try Fried Chicken!',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.TextInput,
                     forms.widgets.Select(choices=TERM_IMPORTANCE_CHOICES)))
        )

    time_and_mode = Cooking_Time(
        label='Cooking Time',
        help_text='30 minutes in total or more?',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.NumberInput,
                     forms.widgets.Select(choices=TIME_CHOICES),
                     forms.widgets.Select(choices=IMPORTANCE_CHOICES)))
        )

    level = forms.MultipleChoiceField(label='Difficulty Level',
                                      choices=LEVEL_CHOICES,
                                      widget=forms.CheckboxSelectMultiple,
                                      required=False)

    calories = forms.MultipleChoiceField(label='Calories',
                                         choices=NUTRITION_CHOICES,
                                         widget=forms.CheckboxSelectMultiple,
                                         required=False)

    fat = forms.MultipleChoiceField(label='Total Fat',
                                    choices=NUTRITION_CHOICES,
                                    widget=forms.CheckboxSelectMultiple,
                                    required=False)

    carb = forms.MultipleChoiceField(label='Total Carbohydrate',
                                     choices=NUTRITION_CHOICES,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)

    protein = forms.MultipleChoiceField(label='Protein',
                                        choices=NUTRITION_CHOICES,
                                        widget=forms.CheckboxSelectMultiple,
                                        required=False)

    sugars = forms.MultipleChoiceField(label='Sugars',
                                       choices=NUTRITION_CHOICES,
                                       widget=forms.CheckboxSelectMultiple,
                                       required=False)

    # show_args = forms.BooleanField(label='Show args_to_ui',
    #                                required=False)


def advance(request):
    context = {}
    res = None
    if request.method == 'GET':
        form = AdvanceForm(request.GET)
        if form.is_valid():
            args = {}
            weight = {}
            if form.cleaned_data['query']:
                args['title'] = form.cleaned_data['query'][0]
                weight['title'] = int(form.cleaned_data['query'][1])

            level = form.cleaned_data['level']
            if level:
                args['level'] = level[0]

            time_and_mode = form.cleaned_data['time_and_mode']
            if time_and_mode:
                print(time_and_mode)
                args['time'] = tuple(time_and_mode[:-1])
                weight['time'] = int(time_and_mode[-1])

            try:
                res = get_dishes(args, weight=weight, nutrient=True)
            except Exception as e:
                print('Exception caught')
                res = None
    else:
        form = AdvanceForm()

    if res is None:
        context['result'] = None
    else:
        columns, result = res
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
        context['form'] = form

    return render(request, 'advance.html', context)

########## SAVE FEATURE ##########
CURRENT_ID = None
class Save(Forms.Form):
    template_name = 'detail.html'

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Product, slug=slug)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("pk")
        product = Product.objects.get(pk=pk)

        if "buy-now" in request.POST:
            #Do something to buy.
            print('buy now ' + product.name)
        elif "add-to-cart" in request.POST:
            #Add to cart.
            print('add to cart ' + product.name)

        return redirect('home')



########## DETAIL PAGE ##########

class NutrientPlot(forms.Form):

    nutrient1 = forms.MultipleChoiceField(label='Nutrient 1',
                                          choices=NUTRITION_PLOT_CHOICE,
                                          widget=forms.CheckboxSelectMultiple,
                                          required=False)

    nutrient2 =  forms.MultipleChoiceField(label='Nutrient 2',
                                           choices=NUTRITION_PLOT_CHOICE,
                                           widget=forms.CheckboxSelectMultiple,
                                           required=False)

def get_detail(request):
    result=request.GET
    recipe_id = int(list(result.keys())[0])
    CURRENT_ID = recipe_id
    recipe = get_dish(recipe_id)
    ingredient = get_dish_ingredient(recipe_id)
    context = dict()
    context['name'] = recipe[1]
    context['time'] = recipe[3]
    context['ingredient'] = ingredient
    context['direction'] = recipe[-1].splitlines()
    # if request.method == 'GET':
    #     form = NutrientPlot(request.GET)
    #     if form.is_valid():
    #         fig1 = plot_one_nutrition(recipe_id, "calories")
    #         fig2 = plot_two_nutrition(recipe_id, "calories", "total_fat")
    #         context['fig1'] = fig1
    #         context['fig2'] = fig2

    # context["form"] = form
    return render(request, 'detail.html', context)
