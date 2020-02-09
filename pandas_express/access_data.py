import sqlite3
import os
import re

DATABASE_FILENAME = '../data/food_map.db'


def search_by_category(categories):
    '''
    To search by categories

    Input:
        categories(list)
    Return:
        results(list)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    args = tuple([x.capitalize() for x in categories if x.lower() not in INDEX_IGNORE])
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
