import sqlite3
import os
import re
import configparser

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']


def current_user(c):
    s = '''
    SELECT * FROM current_user
    '''
    c.execute(s)
    result = c.fetchall()
    return result[0]


def current_dish():
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    s = '''
    SELECT * FROM current_dish
    '''
    c.execute(s)
    result = c.fetchall()
    db.close()
    print('resualhda', result)
    return result[0][0]


def find(c, tbl, id, user):
    s = '''
    SELECT * FROM {}
    WHERE id = ? AND user = ?
    '''.format(tbl)
    c.execute(s, (id, user))
    result = c.fetchall()
    if len(result) > 0:
        return True
    return False


def save(id, tbl='user_fav'):
    '''
    Save result to table
    Input:
        tbl(str): user_fav or user_least_fav
        id(int): food id
        user(str): user name
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    user = current_user(c)[0]
    exist = find(c, tbl, id, user)
    if exist:
        db.close()
        return 'Dish already Saved :)'
    s = '''
    INSERT INTO {} (id, user)
    VALUES (?, ?)
    '''.format(tbl)
    c.execute(s, (id, user))
    db.commit()
    db.close()
    return 'Save Success!'


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


def get_fav():
    s = '''
    SELECT * FROM user_fav
    WHERE user = ?
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    user = current_user(c)
    c.execute(s, (user[0],))
    ids = [item[0] for item in c.fetchall()]
    db.close()
    results = []
    for id in ids:
        results.append(get_dish(id))
    scores = [1 for _ in results]
    return results, scores
