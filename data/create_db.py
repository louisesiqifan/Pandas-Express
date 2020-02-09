'''
To create a relational database for further exploration.

Database Tables:
    TABLE recipes
        id               (unique key, unique)
        names            (str, unique)
        level            (text)
        time_active      (int)
        time_total       (int)
        direction        (text)

    TABLE recipe_categories
        id               (int)
        category_name    (text)

    TABLE recipe_terms
        id               (int)
        term             (text)

    TABLE recipe_title
        id               (int)
        word             (text)

    TABLE recipe_ingredients
        id               (int)
        ingredient_id    (int)

    TABLE ingredients_nutrition
        ingredient_id    (int, unique)
        ingredient_name  (text)
        nutrition_value  (text)

'''

import json
import re
import util
import sqlite3
import numpy as np
from sqlite3 import Error
import configparser
import nutritionix

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
name_db = config['DATA']['NAME_DB']
name_json = config['DATA']['NAME_JSON']
index_ignore = config['DATA']['INDEX_IGNORE']
INGREDIENTS = ['calories', 'total_fat', 'saturated_fat', 'cholesterol',
               'sodium', 'total_carbohydrate', 'dietary_fiber', 'sugars',
               'protein', 'potassium']

def create_table(c, s, name):
    '''
    To create a table from statement s
    '''
    try:
        drop = 'DROP TABLE ' + name + ';'
        c.execute(drop)
        c.execute(s)
    except Error as e:
        c.execute(s)


def write_to_table(c, tb, cols, vals):
    '''
    To write a new row to table
    '''
    l = ['?' for v in vals]
    s = 'INSERT INTO ' + tb + ' ' + \
        str(cols) + ' VALUES ' + '(' + ', '.join(l) + ')'
    c.execute(s, vals)


def time(dic, item):
    '''
    To convert time to minutes
    '''
    t = dic.get(item, '')
    final_t = 0
    hr = re.findall(r"\d+ hr", t)
    if hr != []:
        final_t += 60 * int(hr[0].strip(' hr'))
    min = re.findall(r"\d+ min", t)
    if min != []:
        final_t += int(min[0].strip(' min'))
    return final_t


def clean_time(dic):
    '''
    To make time column uniform: active time and total time in minutes
    '''
    active = time(dic, 'Active') + time(dic, 'Cook') + time(dic, 'Prep')
    total = time(dic, 'Total')
    if total == 0:
        total = active + time(dic, 'Inactive')
    return active, total


def lower_term_from_string(string):
    '''
    To get a list of words from string if words not in INDEX_IGNORE

    Input:
        string(str)
    Return:
        words(list)
    '''
    r = re.findall(r'[a-zA-Z]{2,}', string)
    return set([x.lower() for x in r if x.lower() not in index_ignore])


def get_term(course):
    '''
    To get all terms in the name and descriptions of the course.
    '''
    name = course.get('name')
    directions = course.get('directions', [])
    title = lower_term_from_string(name)
    words = title.copy()
    for direction in directions:
        words = words|set(lower_term_from_string(direction))
    return title, words


def get_nutrient(ingredients, serving_size=1):
    '''
    From ingredients, get ingredients
    '''
    item_list = []
    nutrient = np.array([0]*10)
    for item in ingredients:
        try:
            d = nutritionix.get_nutrient(item)['foods'][0]
        except:
            continue
        name = d.get('food_name', None)
        item_list.append(name)
        for i, key in enumerate(INGREDIENTS):
            k = 'nf_' + key
            val = d.get(k, 0)
            try:
                nutrient[i] += val
            except:
                pass
    nutrient[0] = nutrient[0]/4.184
    return item_list, list(nutrient/serving_size)

def main():
    # Initialize files and strings

    dish = util.read_json(name_json)
    keys = dish.keys()
    sql_create_recipes = config['DATA']['SQL_CREATE_RECIPES']
    sql_create_categories = config['DATA']['SQL_CREATE_CATEGORIES']
    sql_create_terms = config['DATA']['SQL_CREATE_TERMS']
    sql_create_title = config['DATA']['SQL_CREATE_TITLE']
    sql_create_ingredients = config['DATA']['SQL_CREATE_INGREDIENTS']

    # Connect to db
    db = sqlite3.connect(name_db)
    c = db.cursor()

    # Create tables
    create_table(c, sql_create_recipes, 'recipes')
    db.commit()
    create_table(c, sql_create_categories, 'recipe_categories')
    db.commit()
    create_table(c, sql_create_terms, 'recipe_terms')
    db.commit()
    create_table(c, sql_create_title, 'recipe_title')
    db.commit()
    create_table(c, sql_create_ingredients, 'recipe_ingredients')
    db.commit()

    # Write to Tables
    id_tracker = 1
    for k in keys:
        for course in dish[k]:
            name = course.get('name', None)
            level = course.get('level', None)
            if level not in ['Easy', 'Intermediate', 'Advanced']:
                level = 'N/A'
            active, total = clean_time(course.get('time', {}))
            directions = '\n'.join(course.get('directions'))
            ing, nut = get_nutrient(course.get('ingredients'), serving_size=1)
            write_to_table(c, 'recipes',
                               ('id', 'name', 'level',
                                'time_active', 'time_total', 'calories',
                                 'total_fat', 'saturated_fat', 'cholesterol',
                                 'sodium', 'total_carbohydrate',
                                 'dietary_fiber', 'sugars',
                                 'protein', 'potassium', 'directions'),
                               (id_tracker, name, level,
                                active, total, nut[0], nut[1], nut[2], nut[3],
                                nut[4], nut[5], nut[6], nut[7], nut[8], nut[9],
                                directions))
            db.commit()
            for item in ing:
                write_to_table(c, 'recipe_ingredients',
                               ('id', 'ingredient'),
                               (id_tracker, item))
            categories = course.get('categories', [])
            for cat in categories:
                write_to_table(c, 'recipe_categories',
                               ('id', 'category'),
                               (id_tracker, cat))
                db.commit()
            title, words = get_term(course)
            for word in title:
                write_to_table(c, 'recipe_title', ('id', 'word'),
                               (id_tracker, word))
                db.commit()
            for word in words:
                write_to_table(c, 'recipe_terms', ('id', 'word'),
                               (id_tracker, word))
                db.commit()
            id_tracker += 1

    db.close()


if __name__ == '__main__':
    main()
