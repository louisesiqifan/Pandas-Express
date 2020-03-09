import sqlite3
import numpy as np
import pandas as pd
import seaborn as sns
import configparser
import matplotlib.pyplot as plt
from score_assignment import get_dish

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
COLUMNS = ['id', 'name', 'level', 'time_active', 'time_total',
           'serving_size', 'calories', 'total_fat', 'saturated_fat',
           'cholesterol', 'sodium', 'total_carbohydrate',
           'dietary_fiber', 'sugars', 'protein', 'potassium', 'directions']

def get_all_nutrition(nutrition):
    '''
    Get all nutrition from db
    Input:
        nutrition(str)
    Return:
        result(pandas dataframe)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = '''
            SELECT {}
            FROM recipes
            '''.format(nutrition)
    df = pd.read_sql_query(query, db)
    db.close()
    return df


def get_dish_nutrition(id, *args):
    '''
    Get nutrition from args
    Input:
        id(int): course id
        *args(str): nutrition items
    Return:
        nutritions(list): a list of nutrition values
    '''
    nutritions = []
    dish = get_dish(id)
    for arg in args:
        nutritions.append(dish[COLUMNS.index(arg)])
    return nutritions


def plot_one_nutrition(recipe_id, nutrition):
    df = get_all_nutrition(nutrition)
    df = df[df != 0]
    dish_nutrition = get_dish_nutrition(recipe_id, nutrition)
    if dish_nutrition == 0:
        dish_nutrition += 0.0001
    a = plt.figure()
    a = sns.distplot(np.log(df), color="seagreen", bins=20, hist_kws=dict(alpha=0.2))
    a.axvline(x=np.log(dish_nutrition), color="lightcoral")
    a.set_title(nutrition.capitalize())
    output = "static/{}.png".format(nutrition)
    fig = a.get_figure()
    fig.savefig(output)
    return output


def plot_two_nutrition(recipe_id, nutrition1, nutrition2):
    '''
    Plot for two nutritions

    Input:
        id(int): recipe id
        nutrition1(str)
        nutrition2(str)
    '''
    dish_nutrition1, dish_nutrition2 = get_dish_nutrition(recipe_id, nutrition1, nutrition2)
    df1 = get_all_nutrition(nutrition1)
    df2 = get_all_nutrition(nutrition2)
    df1 = df1[(df1[nutrition1] != 0) & (df2[nutrition2] != 0)]
    df2 = df2[(df1[nutrition1] != 0) & (df2[nutrition2] != 0)]
    a = plt.figure()
    a = sns.jointplot(x=np.log(df1), y=np.log(df2), kind="hex",
                      marginal_kws=dict(bins=20, rug=False), color="seagreen")
    if dish_nutrition1 == 0:
        dish_nutrition1 += 0.0001
    if dish_nutrition2 == 0:
        dish_nutrition2 += 0.0001
    a.ax_joint.plot([np.log(dish_nutrition1)], [np.log(dish_nutrition2)],
                    'ro', color='lightcoral')
    output = "static/{}-{}.png".format(nutrition1, nutrition2)
    a.savefig(output)
    return output
