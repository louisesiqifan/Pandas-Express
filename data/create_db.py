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

import re
import sys
import util
import sqlite3
import pandas as pd
from statistics import mean
from sqlite3 import Error
sys.path.append('../pandas_express')

import clean_json
import configparser
from manage_user import create_tables

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
name_db = config['DATA']['NAME_DB']
name_json = config['DATA']['NAME_JSON']
name_ing = config['DATA']['NAME_ING']
index_ignore = config['DATA']['INDEX_IGNORE']
#INGREDIENTS = config['DATA']['INGREDIENTS']

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
    To convert time to minutes.

    Inputs:
        dic: dictionary
        item: "Active"/"Cook"/"Prep"/"Total"

    Outputs:
        final time in minutes: int
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
    To make time column uniform: active time and total time in minutes.

    Inputs:
        dic: dictionary

    Outputs:
        Active: int
        Total time of cooking: int
    '''
    active = time(dic, 'Active') + time(dic, 'Cook') + time(dic, 'Prep')
    total = time(dic, 'Total')
    if total == 0:
        total = active + time(dic, 'Inactive')
    return active, total


def lower_term_from_string(string):
    '''
    To get a list of words from string if words not in INDEX_IGNORE

    Inputs:
        string: str

    Outputs:
        a set of words in string
    '''
    r = re.findall(r'[a-zA-Z]{2,}', string)
    return set([x.lower() for x in r if x.lower() not in index_ignore])


def get_term(course):
    '''
    To get all terms in the name and descriptions of the course.

    Inputs:
        course: dictionary

    Outputs:
        title: set of words in recipe title
        wors: set of words in recipe title and description.
    '''
    name = course.get('name')
    directions = course.get('directions', [])
    title = lower_term_from_string(name)
    words = title.copy()
    for direction in directions:
        words |= set(lower_term_from_string(direction))
    return title, words


def get_serving(course):
    '''
    From course get avg of servings

    Inputs:
        course: dictionary

    Outputs:
        average amount of servings: float
    '''
    def get_mean(ls):
        if ls == []:
            return 1
        else:
            return mean(list(map(int, a)))
    s = course.get('yield', 'no result')
    if s is None:
        s = 'no result'
    a = re.findall(r'\d+', s)
    return get_mean(a)


def get_ingredients_details():
    '''
    '''
    dish = util.read_json(name_json)
    keys = dish.keys()   #123, abc, ..
    sql_create_recipe_detail = config['DATA']['SQL_CREATE_INGREDIENTS_DETAIL']
    db = sqlite3.connect(name_db)
    c = db.cursor()
    create_table(c, sql_create_recipe_detail, 'ingredient_details')
    db.commit()
    id_tracker = 1
    for k in keys:
        for course in dish[k]:
            ingredients = course.get('ingredients', [])
            for ing in ingredients:
                write_to_table(c, 'ingredient_details',
                               ('id', 'ingredient'),
                               (id_tracker, ing))
                db.commit()
            print(id_tracker)
            id_tracker += 1
    db.close()
    print('Finished Creating Ingredients :)')
    return

def main():
    # Initialize files and strings

    dish = util.read_json(name_json)
    keys = dish.keys()   #123, abc, ..
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
    #create_table(c, sql_create_ingredients, 'ingredients')
    #db.commit()

    ig = pd.read_csv('recipe_ing_id.csv')[['recipe_id', 'ing_id']].astype(int)
    #ig.to_sql('recipe_ingredients', db, if_exists='replace', index=False)
    #db.commit()

    # Write to Tables
    foo = clean_json.clean_json_files()  #dictionary
    bar = dict()
    for item in foo.items():
        bar[item[1].id] = item[1]
        """
        obj = item[1]
        write_to_table(c, 'ingredients',
                       ('id', 'ingredient', 'serving_unit',
                        'grams', 'calories', 'total_fat',
                        'saturated_fat', 'cholesterol',
                        'sodium', 'total_carbohydrate',
                        'dietary_fiber', 'sugars',
                        'protein', 'potassium'),
                       (obj.id, obj.name, obj.serving_unit, obj.grams,
                        obj.calories, obj.total_fat, obj.saturated_fat,
                        obj.cholesterol, obj.sodium, obj.total_carbohydrate,
                        obj.dietary_fiber, obj.sugars, obj.protein,
                        obj.potassium))
        """

    id_tracker = 1
    for k in keys:
        for course in dish[k]:
            name = course.get('name', None)
            serving = get_serving(course)
            level = course.get('level', None)
            if level not in ['Easy', 'Intermediate', 'Advanced']:
                level = 'N/A'
            active, total = clean_time(course.get('time', {}))
            directions = '\n'.join(course.get('directions'))
            ings = ig[ig['recipe_id']==id_tracker]['ing_id']
            if len(ings) == 0:
                ings_sum = pd.Series([None]*10)
            else:
                ing_objs = ings.apply(lambda x: bar[x].get_vals())
                ing_vals = pd.DataFrame(ing_objs.tolist())
                ing_sum = ing_vals.sum(axis=0)/serving
            write_to_table(c, 'recipes',
                               ('id', 'name', 'level',
                                'time_active', 'time_total', 'serving_size', 'calories',
                                'total_fat', 'saturated_fat', 'cholesterol',
                                'sodium', 'total_carbohydrate',
                                'dietary_fiber', 'sugars',
                                'protein', 'potassium', 'directions'),
                               (id_tracker, name, level, active,
                                total, serving, ing_sum[0]/4.184, ing_sum[1],
                                ing_sum[2], ing_sum[3], ing_sum[4],
                                ing_sum[5], ing_sum[6], ing_sum[7],
                                ing_sum[8], ing_sum[9], directions))

            db.commit()
#            for item in ing:
#                write_to_table(c, 'recipe_ingredients',
#                               ('id', 'ingredient'),
#                               (id_tracker, item))
#                db.commit()
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
            print(id_tracker)
            id_tracker += 1

    db.close()


if __name__ == '__main__':
    main()
    get_ingredients_details()
    create_tables()
