'''
Python Wrapper fo Nutritionix
Link: https://developer.nutritionix.com/admin/access_details
Doc: https://trackapi.nutritionix.com/docs/
Reference: https://github.com/leetrout/python-nutritionix
'''

import requests
import pandas as pd
import numpy as np
import util

URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

ID = [['95dfa943', '59e2efc1a67da04885a07f8ea16d5114'],
      ['d4366d31', '77c1490af84be97e73a248a2b7bb61ac'],
      ['8b754284', '6cfc07a8ecd4bc61a04729e80d4170f3'],
      ['c96b185b', '1ef46d0ffd3eb437b3938139995538db'],
      ['ceb942f3', 'f8611c9451cda2053e7319b3ae5fe198']]


def get_nutrient(ingredient, headers):
    '''
    Get nutrient informatino of an ingredient

    Inputs:
        ingredient (string)

    Outputs:
        dictionary
    '''
    data = '{"query": "' + ingredient + '", "locale": "en_US"}'
    response = requests.post(URL, headers=headers, data=data)
    return response.json()


def get_nutrient_df(index):
    filename = "ingredient_{}.csv".format(str(index))
    ing_lst = pd.read_csv(filename).key.to_list()
    appid, key = ID[index % 5]
    headers = {"Content-Type": "application/json",
               "x-app-id": appid,
               "x-app-key": key,
               "x-remote-user-id": '0'}
    ing_dict = dict()
    for ing in ing_lst:
        ing_dict[ing] = get_nutrient(ing, headers)

    output = str(index) + ".json"
    util.write_json(ing_dict, output)
