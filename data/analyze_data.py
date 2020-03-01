#%%
import sqlite3
import os
import re
import numpy as np
import pandas as pd
import configparser


NUTRITION_LIST = ['calories', 'total_fat', 'saturated_fat', 'cholesterol', 'sodium', 'total_carbohydrate', 'dietary_fiber', 'sugars', 'protein', 'potassium']
config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
NAME_DB = config['DATA']['NAME_DB']


# def produce_args(nutrition, percentage):
#     '''
#     Produce the args

#     Inputs:
#     nutrition: String
#     percentage: Float
#     '''
#     args = ()
#     args = (percentage, nutrition, nutrition, nutrition)

#     return args

def sql_to_pandas(dbfile='../data/food_map.db'):
    '''
    Convert SQL to Pandas Dataframe
    '''
    con = sqlite3.connect(dbfile)
    myFrames = pd.read_sql_query("SELECT * FROM recipes", con)

    return myFrames


#%%
def get_quantile(nutrition, quantile, c):

    '''
    Helper function to get the quantile for given single nutrition input

    Inputs:
        nutrition: string
        quantile: float
        c: cursor 
    Outputs:
        result: float
    '''
    # args = produce_args(nutrition, quantile)       
    args = (quantile, )
    sql_get_quantile = config['DATA']['SQL_Get_Quantile'].format(nutrition)
    c.execute(sql_get_quantile, args)
    result = c.fetchall()
    return result[0][0]


def get_all_quantile(nut_list=NUTRITION_LIST, quantile_list=[0.33, 0.67]):
    '''
    Get the 33th quantile value and 66th quantile value for each of the nutrition factor in 
    receipe database.

    Inputs:
        nut_list: list of strings
        quantile_list: list of floats

    Outputs:
        dictionary: key: nutrition, value: list of quantile.
    '''
    db = sqlite3.connect(NAME_DB)
    c = db.cursor()
    result = dict()
    for nutrition in nut_list:
        quantiles = []
        for quantile in quantile_list:
            quantiles.append(get_quantile(nutrition, quantile, c))
        result[nutrition] = quantiles

    db.close()
    return result



# %%
