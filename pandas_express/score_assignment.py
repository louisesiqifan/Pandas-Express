import sqlite3
import os
import re
import configparser


config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
INDEX_IGNORE = config['DATA']['INDEX_IGNORE']


def search_by_categories(categories):
    '''
    To search by categories

    Input:
        categories(list)
    Return:
        results(list)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    args = tuple([x.capitalize() for x in categories])
    sub_q = ','.join(['?']*len(args))
    query = f'''
    SELECT r.id, ROUND(k.count*1.0/{len(args)},2) AS score
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


def search_by_level(level):
    level = level.capitalize()
    levels = ['Easy', 'Intermediate', 'Advanced']
    assert level in levels, 'incorrect level'
    ind = levels.index(level)
    val = [int(i<=ind) for i,_ in enumerate(levels)]

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


def search_by_time(upper_bound, mode='total'):
    '''
    to match recipe with input time

    Input:
        upper_bound(int or float)
        mode(str): 'total' or 'active'
    Return:
        results(list): list of tuple with (id, score)
    '''
    assert mode in ['total', 'active'], 'incorrect mode'
    assert upper_bound > 0, 'incorret time constraint'
    upper_bound = str(upper_bound)
    db = sqlite3.connect(DATABASE_FILENAME)
    mode = 'time_' + mode
    c = db.cursor()
    query = f'''
    SELECT id,
        CASE
            WHEN {mode} > 0 AND {mode} < ? THEN 1.0
            WHEN {mode} > 0 AND {mode} >= ? THEN 1.0*(?-{mode})/?
        END AS score
    FROM recipes
    ORDER BY score desc;
    '''
    c.execute(query, (upper_bound,)*4)
    results = c.fetchall()
    db.close()
    return results


def search_by_term(string):
    '''
    to match recipe with input string terms

    Input:
        string(str)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    r = re.findall(r'[a-zA-Z]{2,}', string)
    args = tuple(set([x.lower() for x in r if x.lower() not in INDEX_IGNORE]))
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
