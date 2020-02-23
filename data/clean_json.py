#%%
import json
import glob
import pandas as pd
from sys import platform

class Ingredient:
    def __init__(self, ing_id, ing_name, ing_dict):
        '''
        Constructor for Ingredient object.

        ing_id: int
        ing_name: str
        ing_dict: dictionary
        '''
        self.id = ing_id
        self.name = ing_name
        self.serving_unit = ing_dict.get("serving_unit", 0)
        self.grams = ing_dict.get("serving_weight_grams", 0)
        self.calories = ing_dict.get("nf_calories", 0)
        self.total_fat = ing_dict.get("nf_total_fat", 0)
        self.saturated_fat = ing_dict.get("nf_saturated_fat", 0)
        self.cholesterol = ing_dict.get("nf_cholesterol", 0)
        self.sodium = ing_dict.get("nf_sodium", 0)
        self.total_carbohydrate = ing_dict.get("nf_total_carbohydrate", 0)
        self.dietary_fiber = ing_dict.get("nf_dietary_fiber", 0)
        self.sugars = ing_dict.get("nf_sugars", 0)
        self.protein = ing_dict.get("nf_protein", 0)
        self.potassium = ing_dict.get("nf_potassium", 0)
        self.origin = set()

    def get_vals(self):
        val = (self.calories, self.total_fat, self.saturated_fat,
               self.cholesterol, self.sodium, self.total_carbohydrate,
               self.dietary_fiber, self.sugars, self.protein, self.potassium)
        return val

    def __repr__(self):
        return "<Ingredient {}: {}>".format(self.id, self.name)


def find_json_files():
    '''
    Find all json files

    Inputs:
        None

    Outputs:
        a list of string
    '''
    files = glob.glob('./[0-9]*.json')
    if platform == "win32":
        return [x.strip('.\\') for x in files]
    else:
        return files


def clean_json_files():
    '''
    Clean json files

    Inputs:
        None

    Outputs:
        result: dictionary
    '''
    result = {}
    files = find_json_files()
    id_tracker = 1
    for json_file in files:
        with open(json_file) as f:
            ingredients = json.load(f)
        for origin, item in ingredients.items():
            food = item.get('foods', 3)
            if food == 3:
                continue
            ing_dict = food[0]
            name = ing_dict.get('food_name')
            if name in result:
                ing_obj = result[name]
            else:
                ing_obj = Ingredient(id_tracker, name, ing_dict)
                result[name] = ing_obj
                id_tracker += 1
            ing_obj.origin.add(origin)
    return result


#%%



# %%
