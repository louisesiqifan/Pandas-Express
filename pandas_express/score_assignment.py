import sqlite3
import os
import re
import numpy as np
import pandas as pd
import configparser
from itertools import takewhile
from manage_input import input_verification


config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
INDEX_IGNORE = config['DATA']['INDEX_IGNORE']
NUTRITION_CUT = {'calories': [1.10, 1.25, 1.39],
                 'total_fat':[0.89, 5.06, 13.94],
                 'saturated_fat': [0.16, 1.29, 5.02],
                 'cholesterol': [0.1, 2.45, 50.25],
                 'sodium':[20.41, 121.44, 365.03],
                 'total_carbohydrate': [3.96, 14.88, 34.31],
                 'dietary_fiber': [0.26, 1.22, 2.98],
                 'sugars': [0.58,2.71,8.68],
                 'protein': [1.68, 6.13, 16.43],
                 'potassium': [85.53, 252.0, 463.24]}


def get_one_dish(c, id):
    query = f'''
            SELECT *
            FROM recipes
            WHERE id = {id}
            '''
    c.execute(query)
    result = c.fetchall()[0]
    return result


def get_default_sort(ui_input):
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


def get_dishes(ui_input, lim=10, weight={}):
    score_ranking = score(ui_input, lim, weight)
    dishes = []
    scores = []
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    for id, s in score_ranking:
        dish = get_one_dish(c, id)
        dishes.append(dish)
        scores.append(s)
    db.close()
    columns = ['id', 'name', 'level', 'time_active', 'time_total',
               'serving_size', 'calories', 'total_fat', 'saturated_fat',
               'cholesterol', 'sodium', 'total_carbohydrate',
               'dietary_fiber', 'sugars', 'protein', 'potassium', 'directions']
    df = pd.DataFrame(dishes, columns=columns)
    df['score'] = scores
    sort_list, order = get_default_sort(ui_input)
    return df.sort_values(sort_list, ascending=order)[:lim]


def score(ui_input, lim, weight):
    '''
    From ui_input, update score and show the top records

    Input:
        ui_input(dict)
        lim(int)
        weight(dictionary)
    Return:
        top(list)
    '''
    score  = {}
    ui_input = input_verification(ui_input)
    category = ui_input.get('categories', False)
    level = ui_input.get('level', False)
    time_params = ui_input.get('time', False)
    term = ui_input.get('term', False)
    title = ui_input.get('title', False)
    nutrition = ui_input.get('nutrition', False)
    if category:
        result = search_by_categories(category)
        for i, val in result:
            score[i] = score.get(i, 0) + val*weight.get('categories',1)
    if level:
        result = search_by_level(level)
        for i, val in result:
            score[i] = score.get(i, 0) + val*weight.get('level',1)
    if time_params:
        result = search_by_time(time_params)
        for i, val in result:
            if val:
                score[i] = score.get(i, 0) + val*weight.get('time',1)
    if term:
        result = search_by_term(term)
        for i, val in result:
            score[i] = score.get(i, 0) + val*weight.get('term',1)
    if title:
        result = search_by_title(title)
        for i, val in result:
            s = score.get(i, 0) + val*weight.get('title',10)
            score[i] = s
    if nutrition:
        result = search_by_nutrition(nutrition)
        for i, val in result:
            s = score.get(i, 0) + val*weight.get('nutrition',1)
            score[i] = s
    final_score = sorted(score.items(),
                         key=lambda item: item[1], reverse=True)
    last = final_score[lim][1]
    result = takewhile(lambda x: x[1]>=last, final_score)
    return result


def search_by_categories(args):
    '''
    To search by categories

    Input:
        args(list)
    Return:
        results(list)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    sub_q = ','.join(['?']*len(args))
    query = f'''
    SELECT r.id AS id, ROUND(k.count*1.0/{len(args)},2) AS score
    FROM recipes AS r
    JOIN (SELECT id, COUNT(id) AS count
          FROM recipe_categories
          WHERE category IN ({sub_q})
          GROUP BY id) AS k
          ON k.id = r.id
    '''
    c.execute(query, args)
    results = c.fetchall()
    db.close()
    return results


def search_by_level(val):
    '''
    to match recipe with input level

    Input:
        val(list):
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = f'''
    SELECT id,
           CASE
               WHEN level = 'Easy' THEN {val[0]}
               WHEN level = 'Intermediate' THEN {val[1]}
               WHEN level = 'Advanced' THEN {val[2]}
           END AS score
    FROM recipes
    WHERE score IS NOT NULL;
    '''
    c.execute(query)
    results = c.fetchall()
    db.close()
    return results


def search_by_time(time_params):
    '''
    to match recipe with input time

    Input:
        time_params(tuple): (upper_bound, mode)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    upper_bound, mode = time_params
    mode = 'time_' + mode
    c = db.cursor()
    query = f'''
    SELECT id,
        CASE
            WHEN {mode} > 0 AND {mode} <= ? THEN 1.0
            WHEN {mode} > 0 AND {mode} > ? THEN 1.0*(?-{mode})/?
        END AS score
    FROM recipes
    ORDER BY score desc;
    '''
    c.execute(query, (upper_bound,)*4)
    results = c.fetchall()
    db.close()
    return results


def search_by_title(args):
    '''
    to match recipe with input string terms

    Input:
        args(list)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    args_dup = [x for x in args for _ in range(2)]
    case = '''
    CASE
        WHEN INSTR(name, ?) > 0 THEN 1
        ELSE 0
    END
    '''
    plus_string = '+'.join([case]*len(args))
    query = f'''
    SELECT id, ROUND(({plus_string})*1.0/{len(args)},2) AS score
    FROM recipes
    ORDER BY score desc;
    '''
    c.execute(query, tuple(args))
    results = c.fetchall()
    db.close()
    return results


def search_by_term(args):
    '''
    to match recipe with input string terms

    Input:
        string(list)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    sub_q = ','.join(['?']*len(args))
    query = f'''
        SELECT id, ROUND(COUNT(id)*1.0/{len(args)},2) AS score
        FROM recipe_terms
        WHERE word IN ({sub_q})
        GROUP BY id
        ORDER BY score desc;
        '''
    c.execute(query, args)
    results = c.fetchall()
    db.close()
    return results


def search_by_nutrition(arg_dict):
    '''
    to find recipes that satisfy nutrition needs

    Input:
        args (dict):
            key: which nutrition item
            val: sides (-1: want lower; 1: want higher)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    args = []
    l = len(arg_dict.keys())
    for item, side in arg_dict.items():
        cuts = NUTRITION_CUT[item]
        arg = [item, cuts[2], side, item, cuts[0], 0-side]
        args = args + arg
    case = '''
    CASE
        WHEN ? > ? THEN ?
        WHEN ? < ? THEN ?
        ELSE 0
    END
    '''
    plus_string = '+'.join([case]*l)
    query = f'''
            SELECT id, ROUND(({plus_string})*1.0/{l},2) AS score
            FROM recipes
            ORDER BY score desc;
            '''
    c.execute(query, tuple(args))
    results = c.fetchall()
    db.close()
    return results



###########
EXAMPLE_0 = {'level': 'easy',
             'time': (30, 'total'), 'title': 'fried chicken',
             'nutrition': {'calories': -1, 'protein': 1}}
