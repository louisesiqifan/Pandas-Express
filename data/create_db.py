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
from sqlite3 import Error


INDEX_IGNORE = ['the', 'and', 'to', 'with', 'in', 'of', 'until',
                'minutes', 'add', 'heat', 'for', 'on', 'into', 'over', 'salt',
                'medium', 'about', 'cook', 'bowl', 'large', 'pan', 'is', 'top',
                'oil', 'or', 'from', 'stir', 'each', 'it', 'place', 'oven',
                'remove', 'mixture', 'skillet', 'water', 'serve', 'minute',
                'high', 'inch', 'combine', 'remaining', 'then', 'up', 'set',
                'cup', 'together', 'cut', 'cover', 'preheat', 'mix', 'an',
                'stirring', 'degrees', 'baking', 'hot', 'side', 'at', 'simmer',
                'let', 'are', 'sheet', 'cool', 'small', 'teaspoon', 'all',
                'layer', 'bring', 'boil', 'half', 'transfer', 'by', 'them',
                'if', 'put', 'tablespoons', 'as', 'out', 'aside', 'through',
                'spoon', 'be', 'pot', 'more', 'lightly', 'pour']

def create_table(c, s):
    '''
    To create a table from statement s
    '''
    try:
        c.execute(s)
    except Error as e:
        print(e)


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


def get_term(course):
    '''
    To get all terms in the name and descriptions of the course.
    '''



def main():
    # Initialize files and strings
    dish = util.read_json("foodnetwork.json")
    keys = dish.keys()
    file_name = 'food_map.db'
    table_maps = {'recipes': ('id', 'name', 'level', 'time_active', 'time_total'),
                  'categories': ('id', 'category')}
    sql_create_recipes = '''
                         CREATE TABLE IF NOT EXISTS recipes (
                              id integer PRIMARY KEY,
                              name text NOT NULL,
                              level text NOT NULL,
                              time_active integer,
                              time_total integer
                              );
                                                        '''
    sql_create_categories = '''
                         CREATE TABLE IF NOT EXISTS recipe_categories (
                              id integer,
                              category text NOT NULL
                              );
                                                        '''
    sql_create_terms = '''
                         CREATE TABLE IF NOT EXISTS recipe_terms (
                              id integer,
                              term text NOT NULL
                              );
                                                        '''
    # Connect to db
    db = sqlite3.connect(file_name)
    c = db.cursor()

    # Create tables
    create_table(c, sql_create_recipes)
    db.commit()
    create_table(c, sql_create_categories)
    db.commit()
    create_table(c, sql_create_terms)
    db.commit()

    # Write to Tables
    id_tracker = 0
    for k in keys:
        for course in dish[k]:
            name = course.get('name', None)
            level = course.get('level', None)
            if level not in ['Easy', 'Intermediate', 'Advanced']:
                level = 'N/A'
            active, total = clean_time(course.get('time', {}))
            try:
                write_to_table(c, 'recipes',
                               ('id', 'name', 'level',
                                'time_active', 'time_total'),
                               (id_tracker, name, level, active, total))
            except:
                continue
            db.commit()
            categories = course.get('categories', [])
            for cat in categories:
                write_to_table(c, 'recipe_categories',
                               ('id', 'category'),
                               (id_tracker, cat))
                db.commit()
            id_tracker += 1

    db.close()


if __name__ == '__main__':
    main()
