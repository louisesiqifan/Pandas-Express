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

    TABLE recipe_Ingredients
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
    s = 'INSERT INTO ' + tb + ' ' + str(cols) + ' VALUES ' +'(' + ', '.join(l) + ')'
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
    if dic is None:
        return 0, 0

    keys = ['Active', 'Cook', 'Inactive', 'Prep', 'Total']
    active = time(dic, 'Active') + time(dic, 'Cook') + time(dic, 'Prep')
    total = time(dic, 'Total')
    if total == 0:
        total = active + time(dic, 'Inactive')
    return active, total



def main():
    ### Initialize files and strings
    dish = util.read_json("foodnetwork.json")
    keys = dish.keys()
    file_name = 'food_map.db'
    table_maps = {'recipes': ('id', 'name','level', 'time_active', 'time_total'),
                  'categories': ('id', 'category')}
    sql_create_recipes = '''
                         CREATE TABLE IF NOT EXISTS recipes (
                              id integer PRIMARY KEY,
                              name text NOT NULL,
                              level text,
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
    ### Connect to db
    db = sqlite3.connect(file_name)
    c = db.cursor()

    ### Create tables
    create_table(c, sql_create_recipes)
    db.commit()
    create_table(c, sql_create_categories)
    db.commit()

    ### Write to Tables
    id_tracker = 0
    for k in keys:
        for course in dish[k]:
            name = course.get('name', None)
            level = course.get('level', None)
            active, total = clean_time(course.get('time', None))
            write_to_table(c, 'recipes',
                           ('id', 'name','level', 'time_active', 'time_total'),
                           (id_tracker, name, level, active, total))
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
