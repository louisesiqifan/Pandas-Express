import sqlite3
import os
import sys
import numpy as np
import pandas as pd
import configparser
from itertools import takewhile
from manage_input import input_verification
from user_preference import get_fav


config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
INDEX_IGNORE = config['DATA']['INDEX_IGNORE']
NUTRITION_CUT = {'calories': [4.2224346717654555, 15.087066375307291],
                 'total_fat': [0.2175, 2.283333333333333],
                 'saturated_fat': [0.04428571428571428, 0.7488888888888889],
                 'cholesterol': [0.0, 6.658333333333334],
                 'sodium': [6.243333333333333, 64.02222222222223],
                 'total_carbohydrate': [0.8729166666666667, 5.825],
                 'dietary_fiber': [0.0625, 0.535],
                 'sugars': [0.13, 1.4400000000000002],
                 'protein': [0.36000000000000004, 2.648888888888889],
                 'potassium': [19.033333333333335, 85.02399999999999]}

COLUMNS = ['id', 'name', 'level', 'time_active', 'time_total',
           'serving_size', 'calories', 'total_fat', 'saturated_fat',
           'cholesterol', 'sodium', 'total_carbohydrate',
           'dietary_fiber', 'sugars', 'protein', 'potassium', 'directions']


def search_by_title(c, terms):
    '''
    Search recipe by input string terms

    Inputs:
        c: sqlite3.Cursor
        terms: list of strings

    Return:
        results: list of (id, score)
    '''
    case = '''
    CASE
        WHEN INSTR(name, ?) > 0 THEN 1
        ELSE 0
    END
    '''
    N = len(terms)
    plus_string = '+'.join([case] * N)
    query = '''
    SELECT id, ROUND(({}) * 1.0 / {}, 2) AS score
    FROM recipes
    ORDER BY score desc;
    '''.format(plus_string, N)
    params = tuple(terms)
    c.execute(query, params)
    results = c.fetchall()
    return results


def search_by_term(c, terms):
    '''
    to match recipe with input string terms

    Inputs:
        c: sqlite3.Cursor
        terms: list of strings

    Return:
        results: list of (id, score)
    '''
    N = len(terms)
    sub_q = ','.join(['?'] * N)
    query = '''
    SELECT id, ROUND(COUNT(id) * 1.0 / {}, 2) AS score
    FROM recipe_terms
    WHERE word IN ({})
    GROUP BY id
    ORDER BY score desc;
    '''.format(N, sub_q)
    params = tuple(terms)
    c.execute(query, params)
    results = c.fetchall()
    return results


def search_by_level(c, level_val):
    '''
    Search recipe by input level

    Inputs:
        c: sqlite3.Cursor
        level_val: [1, 0, 0] / [0, 1, 0]/ [0, 0, 1]

    Outputs:
        results: list of (id, score)
    '''
    query = '''
    SELECT id,
        CASE
            WHEN level = 'Easy' THEN ?
            WHEN level = 'Intermediate' THEN ?
            WHEN level = 'Advanced' THEN ?
        END AS score
    FROM recipes
    WHERE score IS NOT NULL;
    '''
    params = tuple(level_val)
    c.execute(query, params)
    results = c.fetchall()
    return results


def search_by_time(c, time_params):
    '''
    Search recipe by input time

    Inputs:
        c: sqlite3.Cursor
        time_params(tuple): (upper_bound, mode)

    Outputs:
        results: list of (id, score)
    '''
    upper_bound, mode = time_params
    mode = 'time_' + mode
    query = '''
    SELECT id,
        CASE
            WHEN {0} > 0 AND {0} <= ? THEN 1.0
            WHEN {0} > 0 AND {0} > ? THEN 1.0*(?-{0})/?
        END AS score
    FROM recipes
    ORDER BY score desc;
    '''.format(mode)
    params = (upper_bound,)*4
    c.execute(query, params)
    results = c.fetchall()
    return results


def search_by_nutrition(c, arg_dict):
    '''
    Search recipes by nutrition needs

    Inputs:
        c: sqlite3.Cursor
        arg_dict:
            key: which nutrition item
            val: sides (-1: want lower; 1: want higher)

    Return:
        results: list of (id, score)
    '''
    args = []
    l = len(arg_dict.keys())
    for item, side in arg_dict.items():
        cuts = NUTRITION_CUT[item]
        arg = [item, cuts[1], side, item, cuts[0], 0-side]
        args = args + arg
    case = '''
    CASE
        WHEN ? > ? THEN ?
        WHEN ? < ? THEN ?
        ELSE 0
    END
    '''
    plus_string = '+'.join([case]*l)
    query = '''
    SELECT id, ROUND(({}) * 1.0 / {}, 2) AS score
    FROM recipes
    ORDER BY score desc;
    '''.format(plus_string, l)
    c.execute(query, tuple(args))
    results = c.fetchall()
    return results


def update_score(args_to_ui, lim, weight):
    '''
    From ui_input, update score and show the top records

    Inputs:
        c: sqlite3.Cursor
        args_to_ui: dict
        lim: int
        weight: dictionary

    Outputs:
        result: list
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    score = {}
    ui_input = input_verification(args_to_ui)
    level = ui_input.get('level', False)
    time_params = ui_input.get('time', False)
    title = ui_input.get('title', False)
    terms = ui_input.get('term', False)
    nutrition = ui_input.get('nutrition', False)
    if level:
        result = search_by_level(c, level)
        for i, val in result:
            score[i] = score.get(i, 0) + val * weight.get('level', 1)
    if time_params:
        result = search_by_time(c, time_params)
        for i, val in result:
            if val:
                score[i] = score.get(i, 0) + val * weight.get('time', 1)
    if title:
        result = search_by_term(c, terms)
        for i, val in result:
            score[i] = score.get(i, 0) + val * weight.get('term', 1)
        result = search_by_title(c, title)
        for i, val in result:
            s = score.get(i, 0) + val*weight.get('title', 10)
            score[i] = s
    if nutrition:
        result = search_by_nutrition(c, nutrition)
        for i, val in result:
            s = score.get(i, 0) + val*weight.get('nutrition', 1)
            score[i] = s
    final_score = sorted(score.items(), key=lambda item: item[1], reverse=True)
    last = final_score[lim][1]
    result = takewhile(lambda x: x[1] >= last, final_score)
    db.close()
    return result


def get_default_sort(ui_input):
    '''
    Inputs:
        ui_input: dictinoary

    Outputs:
        sort_list: list of string
        order: list of boolean
    '''
    sort_list = ['score']
    order = [False]
    nut = ui_input.get('nutrition', None)
    if nut is not None:
        for k, v in nut.items():
            sort_list.append(k)
            if v == 1:
                order.append(False)
            else:
                order.append(True)
    sort_list.append('level')
    order.append(True)
    return sort_list, order


def get_dish(recipe_id):
    '''
    Get a dish by id.

    Inputs:
        recipe_id: int

    Outputs:
        result: tuple
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = '''
    SELECT *
    FROM recipes
    WHERE id = ?
    '''
    params = (recipe_id, )
    c.execute(query, params)
    result = list(c.fetchall()[0])
    for i, e in enumerate(result):
        if isinstance(e, float):
            result[i] = round(e, 2)
    db.close()
    return tuple(result)


def get_dish_ingredient(recipe_id):
    '''
    Get dish ingredient by id
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = '''
    SELECT ingredient
    FROM ingredient_details
    WHERE id = ?
    '''
    params = (recipe_id, )
    c.execute(query, params)
    result = c.fetchall()
    db.close()
    ing_list = []
    for sentence in result:
        ing_list.append(sentence[0])
    return ing_list


def feeling_lucky():
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = 'SELECT COUNT(*) FROM recipes'
    c.execute(query)
    max_length = c.fetchall()[0]
    i = int(np.random.randint(1, max_length))
    db.close()
    return get_dish(i)


def get_dishes(args_to_ui, lim=10, weight={}, debug=False, nutrient=False, fav=False):
    '''
    Get all dishes.

    Inputs:
        ui_input: dictionary
        lim: int
        weight: dict
        debug: boolean

    Outputs:
        [columns: list, dishes: list of tuples ]
    '''
    if fav:
        dishes, scores = get_fav()
    else:
        if not args_to_ui:
            return [[], []]

        score_ranking = update_score(args_to_ui, lim, weight)
        dishes = []
        scores = []
        for recipe_id, score in score_ranking:
            dish = get_dish(recipe_id)
            dishes.append(dish)
            scores.append(score)

    df = pd.DataFrame(dishes, columns=COLUMNS)
    df['score'] = scores
    sort_list, order = get_default_sort(args_to_ui)
    df = df.sort_values(sort_list, ascending=order)[:lim]
    if debug:
        print(df)

    for key, val in NUTRITION_CUT.items():
        df[key] = df[key].apply(lambda x: 'low' if x < val[0]
                                else ('high' if x > val[1] else 'med'))

    cols = ['name', 'level', 'time_active', 'time_total', 'id']
    if nutrient:
        cols = ['name', 'level', 'time_active', 'time_total',
                'calories', 'total_fat', 'total_carbohydrate',
                'sugars', 'protein', 'id']
    df = df[cols]
    tuples = [tuple(x) for x in df.to_numpy()]
    return [cols, tuples]


###########
EXAMPLE_0 = {'level': 'easy',
             'time': (30, 'total'), 'title': 'fried chicken',
             'nutrition': {'calories': -1, 'protein': 1}}
