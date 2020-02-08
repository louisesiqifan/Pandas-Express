import sqlite3
import os

DATABASE_FILENAME = '../0_Data/food_map.db'

def search_by_category(category):
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = '''
    SELECT recipes.name 
    FROM recipes JOIN recipe_categories ON recipe_categories.id = recipes.id
    WHERE recipe_categories.category = ?
    '''
    params = (category, )
    c.execute(query, params)
    results = c.fetchall()
    db.close()
    return results