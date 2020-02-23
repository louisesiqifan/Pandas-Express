import pandas as pd
import numpy as np
import util
import configparser


config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
name_json = config['DATA']['NAME_JSON']

def rid_to_ing():
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
    return ori
