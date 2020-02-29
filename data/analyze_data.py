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
name_db = config['DATA']['NAME_DB']

result_list = []


def produce_args(nutrition, percentage):
    '''
    Produce the args

    Inputs:
    nutrition: String
    percentage: Float
    '''
    args = ()
    args = (str(percentage), nutrition, nutrition, nutrition, nutrition)

    return args

def sql_to_pandas():
    '''
    Convert SQL to Pandas Dataframe
    '''
    con = sqlite3.connect('../data/food_map.db')
    myFrames = pd.read_sql_query("SELECT * FROM recipes", con)

    return myFrames

def get_33th_quantile (NUTRITION_LIST):
    '''
    Get the 33th quantile value and 66th quantile value for each of the nutrition factor in 
    receipe database.
    '''

    for nutrition in NUTRITION_LIST:
        args = produce_args(nutrition, 0.33)       
        sql_get_quantile = config['DATA']['SQL_Get_Quantile']
        db = sqlite3.connect(name_db)
        c = db.cursor()
        print(args)
        print(sql_get_quantile)
        c.execute(sql_get_quantile, args)
        results = c.fetchall()
        print(results)
        result_list.append(results)
    
    return result_list


#def get_66th_quantile (NUTRITION_LIST):
    '''
    Get the 33th quantile value and 66th quantile value for each of the nutrition factor in 
    receipe database.
    '''
 #   for nutrition in NUTRITION_LIST:
  #      args = produce_args(nutrition, 0.66)       
   #     sql_get_quantile = config['DATA']['SQL_Get_Quantile']
    #    # Connect to db
     #   c = db.cursor()
      #  c.execute(sql_get_quantile, args)
       # db = sqlite3.connect(name_db)
        #c = db.cursor()
       # results = c.fetchall()
        #result_list.append(results)
    
    return result_list

# %%
get_33th_quantile(NUTRITION_LIST)

# %%
