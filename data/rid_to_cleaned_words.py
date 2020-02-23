#%%
import pandas as pd
import numpy as np
import util
import configparser
from clean_json import clean_json_files


config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
name_json = config['DATA']['NAME_JSON']

def recipe_id_to_ing():
    '''
    Create a dataframe with recipe id and ingredients
    '''
    ori = {}
    dish = util.read_json(name_json)
    clean = pd.read_csv('cleaned_ingredients.csv',
                        names=['id', 'origin', 'n', 'q', 'cleaned'],
                        sep='|')
    clean = clean[clean['cleaned'].notna()]
    keys = dish.keys()
    id_tracker = 1
    for k in keys:
        for course in dish[k]:
            ings = course.get("ingredients", [])
            for ing in ings:
                ing = ing.replaceAll('�', '')
                result = clean[clean['origin'] == ing]
                if len(result) > 0:
                    ori[result.iloc[0]['cleaned']] = id_tracker
            id_tracker += 1
            
    df = pd.DataFrame.from_dict(ori, orient='index').reset_index()
    df.columns = ["origin", "recipe_id"]
    return df


def get_ing_df():
    '''
    Create an ingredient dataframe
    
    Inputs: 
        result: dictionary
    
    Outputs:
        Pandas Dataframe
    '''
    result = clean_json_files()
    ing_lst = []
    for ing in result:
        ing_obj = result[ing]
        origin = ing_obj.origin
        for key in origin:
            ing_lst.append((key, ing_obj.name, ing_obj.id))

    return pd.DataFrame(ing_lst, columns=["origin", "ing_name", "ing_id"])


def recipe_ing_id():
    df1 = recipe_id_to_ing()
    df2 = get_ing_df()
    df = df1.merge(df2, on='origin', how='left')
    df = df[['recipe_id', 'ing_id']]
    return df
    

# %%
