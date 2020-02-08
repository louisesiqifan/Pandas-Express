import sqlite3
import os
import re

DATABASE_FILENAME = '../data/food_map.db'

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

def search_by_category(category):
    category = category.capitalize()
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = '''
    SELECT recipes.id
    FROM recipes JOIN recipe_categories ON recipe_categories.id = recipes.id
    WHERE recipe_categories.category = ?
    '''
    params = (category, )
    c.execute(query, params)
    results = c.fetchall()
    db.close()
    return results


def search_by_time(upper_bound, mode='total'):
    assert mode in ['total', 'active'], 'incorrect mode'
    db = sqlite3.connect(DATABASE_FILENAME)
    mode = 'time_' + mode
    c = db.cursor()
    query = f'''
    SELECT id, ?-{mode} AS score
    FROM recipes
    WHERE {mode} > 0
    ORDER BY score desc;
    '''
    c.execute(query, (upper_bound,))
    results = c.fetchall()
    db.close()
    return results


def search_by_term(string):
    '''
    to match recipe with input string terms

    Input:
        string(str)
    Return:
        results(list): list of tuple with (id, count)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    r = re.findall(r'[a-zA-Z]{2,}', string)
    args = tuple(set([x.lower() for x in r if x.lower() not in INDEX_IGNORE]))
    sub_q = ','.join(['?']*len(args))
    query = f'''
    SELECT id, COUNT(id) AS score
    FROM recipe_terms
    WHERE word IN ({sub_q})
    GROUP BY id
    ORDER BY score desc;
    '''
    c.execute(query, args)
    results = c.fetchall()
    db.close()
    return results
